#!/usr/bin/env python3
"""
RAG Pipeline für den Learning Hub.
Verwendet: ChromaDB (installiert) + Gemini Embeddings (REST API).
Keine neuen Pakete nötig — alles schon im Container.

Komponenten:
1. ingest.py — Content chunken, embedden, in ChromaDB speichern
2. query.py — Semantische Suche über alle Lerninhalte
3. build_rag.py — Orchestrator (einmal laufen lassen zum Index-Aufbau)
"""
import os
import json
import sys
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Optional

import requests
import chromadb
from chromadb.config import Settings

# ── Config ───────────────────────────────────────────────
WORKSPACE = "/data/.openclaw/workspace"
CONTENT_DIR = f"{WORKSPACE}/projects/learning-hub/content"
CHROMA_DIR = f"{WORKSPACE}/projects/learning-hub/.chroma"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
EMBEDDING_MODEL = "gemini-embedding-001"  # 3072 dims, free tier
EMBEDDING_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBEDDING_MODEL}:embedContent"

# ── Gemini Embeddings via REST ─────────────────────────────
def get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """Get embedding vector from Gemini API."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")
    
    resp = requests.post(
        f"{EMBEDDING_URL}?key={GEMINI_API_KEY}",
        json={
            "model": f"models/{EMBEDDING_MODEL}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["embedding"]["values"]


# ── Chunking ──────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks on sentence boundaries."""
    import re
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Start new chunk with overlap from previous
            words = current_chunk.split() if current_chunk else []
            overlap_text = " ".join(words[-overlap//10:]) if words else ""
            current_chunk = overlap_text + " " + sentence if overlap_text else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def flatten_content(content_dir: str) -> List[Dict]:
    """Read all JSON books and flatten into searchable documents."""
    documents = []
    
    for track_dir in Path(content_dir).iterdir():
        if not track_dir.is_dir():
            continue
        track_id = track_dir.name
        
        for book_file in track_dir.glob("*.json"):
            try:
                with open(book_file) as f:
                    book = json.load(f)
            except Exception as e:
                print(f"  ⚠️ Fehler beim Lesen von {book_file}: {e}", file=sys.stderr)
                continue
            
            book_id = book.get("id", book_file.stem)
            book_title = book.get("title", book_id)
            book_author = book.get("author", "")
            book_source = book.get("source_url", "")
            
            for chapter in book.get("chapters", []):
                chapter_id = chapter.get("id", "")
                chapter_title = chapter.get("title", "")
                
                # ── Flashcards as documents ──
                for i, card in enumerate(chapter.get("flashcards", [])):
                    front = card.get("front", "")
                    back = card.get("back", "")
                    full_text = f"Frage: {front}\nAntwort: {back}"
                    
                    documents.append({
                        "id": f"{track_id}/{book_id}/{chapter_id}/flashcard-{i}",
                        "text": full_text,
                        "metadata": {
                            "track_id": track_id,
                            "book_id": book_id,
                            "book_title": book_title,
                            "book_author": book_author,
                            "chapter_id": chapter_id,
                            "chapter_title": chapter_title,
                            "type": "flashcard",
                            "source_url": book_source,
                        },
                        "chunks": [],  # filled below
                    })
                
                # ── Quiz as documents ──
                for i, q in enumerate(chapter.get("quiz", [])):
                    question = q.get("question", "")
                    options = q.get("options", [])
                    explanation = q.get("explanation", "")
                    correct_idx = q.get("correct", -1)
                    correct_answer = options[correct_idx] if 0 <= correct_idx < len(options) else ""
                    
                    full_text = f"Frage: {question}\nOptionen: {' | '.join(options)}\nRichtige Antwort: {correct_answer}\nErklärung: {explanation}"
                    
                    documents.append({
                        "id": f"{track_id}/{book_id}/{chapter_id}/quiz-{i}",
                        "text": full_text,
                        "metadata": {
                            "track_id": track_id,
                            "book_id": book_id,
                            "book_title": book_title,
                            "book_author": book_author,
                            "chapter_id": chapter_id,
                            "chapter_title": chapter_title,
                            "type": "quiz",
                            "source_url": book_source,
                        },
                        "chunks": [],
                    })
            
            print(f"  ✓ {track_id}/{book_id}: {len(chapter.get('flashcards',[]))} Karten, {len(chapter.get('quiz',[]))} Quiz", file=sys.stderr)
    
    # ── Chunk each document ──
    for doc in documents:
        doc["chunks"] = chunk_text(doc["text"])
    
    return documents


# ── Ingest into ChromaDB ──────────────────────────────────
def build_index(content_dir: str, chroma_dir: str, batch_size: int = 50):
    """Build complete RAG index from content files."""
    
    print("=" * 60, file=sys.stderr)
    print("📚 RAG Pipeline — Learning Hub", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # 1. Flatten content
    print("\n📖 Lese Content-Dateien...", file=sys.stderr)
    documents = flatten_content(content_dir)
    print(f"\n   {len(documents)} Dokumente gefunden", file=sys.stderr)
    
    # 2. Prepare all chunks
    all_chunks = []
    for doc in documents:
        for i, chunk in enumerate(doc["chunks"]):
            if len(chunk.strip()) < 20:
                continue
            all_chunks.append({
                "id": f"{doc['id']}-chunk-{i}",
                "text": chunk,
                "doc_id": doc["id"],
                "metadata": {**doc["metadata"], "chunk_index": i, "total_chunks": len(doc["chunks"])},
            })
    
    print(f"   {len(all_chunks)} Chunks zum Einbetten", file=sys.stderr)
    
    # 3. Setup ChromaDB
    chroma_client = chromadb.PersistentClient(path=chroma_dir, settings=Settings(anonymized_telemetry=False))
    
    # Delete existing collection to rebuild fresh
    try:
        chroma_client.delete_collection("learning_content")
    except Exception:
        pass
    
    collection = chroma_client.create_collection(
        name="learning_content",
        metadata={"description": "Learning Hub RAG Index — CFO Finance + SAP S/4HANA Content"},
    )
    
    # 4. Embed and store in batches
    print(f"\n🧠 Erstelle Embeddings (Gemini text-embedding-004)...", file=sys.stderr)
    print(f"   Batch-Größe: {batch_size}, Insgesamt: {len(all_chunks)} Chunks", file=sys.stderr)
    
    for batch_start in range(0, len(all_chunks), batch_size):
        batch = all_chunks[batch_start:batch_start + batch_size]
        
        ids = []
        documents_texts = []
        metadatas = []
        
        # Get embeddings one by one (Gemini REST doesn't support batches nicely)
        embeddings = []
        for chunk in batch:
            try:
                emb = get_embedding(chunk["text"])
                embeddings.append(emb)
                ids.append(chunk["id"])
                documents_texts.append(chunk["text"])
                metadatas.append(chunk["metadata"])
            except Exception as e:
                print(f"  ⚠️ Embedding-Fehler für {chunk['id'][:50]}: {e}", file=sys.stderr)
                time.sleep(1)
        
        if embeddings:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents_texts,
                metadatas=metadatas,
            )
        
        progress = min(batch_start + batch_size, len(all_chunks))
        print(f"  [{progress}/{len(all_chunks)}] {(progress/len(all_chunks)*100):.1f}%", file=sys.stderr)
        
        # Rate limit pause
        if batch_start + batch_size < len(all_chunks):
            time.sleep(0.5)
    
    print(f"\n✅ Index fertig: {collection.count()} Chunks in ChromaDB", file=sys.stderr)
    print(f"   Pfad: {chroma_dir}", file=sys.stderr)
    
    return collection


# ── Query ─────────────────────────────────────────────────
def query_rag(query_text: str, chroma_dir: str, n_results: int = 5):
    """Semantic search over learning content."""
    
    chroma_client = chromadb.PersistentClient(path=chroma_dir, settings=Settings(anonymized_telemetry=False))
    
    try:
        collection = chroma_client.get_collection("learning_content")
    except Exception:
        print("❌ Kein Index gefunden. Bitte zuerst build_rag.py ausführen.", file=sys.stderr)
        return []
    
    # Get query embedding
    query_embedding = get_embedding(query_text, task_type="RETRIEVAL_QUERY")
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )
    
    hits = []
    for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
        results["ids"][0], 
        results["documents"][0], 
        results["metadatas"][0],
        results["distances"][0],
    )):
        hits.append({
            "rank": i + 1,
            "id": doc_id,
            "text": doc_text,
            "metadata": metadata,
            "score": 1.0 - distance,  # ChromaDB returns distance, convert to similarity
        })
    
    return hits


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Learning Hub RAG Pipeline")
    parser.add_argument("command", choices=["build", "query", "stats"], help="Aktion")
    parser.add_argument("query", nargs="?", help="Suchbegriff (nur für 'query')")
    parser.add_argument("--batch-size", type=int, default=50, help="Embedding Batch-Größe")
    parser.add_argument("--results", type=int, default=5, help="Anzahl Ergebnisse")
    
    args = parser.parse_args()
    
    if args.command == "build":
        build_index(CONTENT_DIR, CHROMA_DIR, args.batch_size)
    
    elif args.command == "stats":
        chroma_client = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False))
        try:
            collection = chroma_client.get_collection("learning_content")
            print(f"Collection: {collection.name}")
            print(f"Documents:  {collection.count()}")
        except Exception:
            print("❌ Kein Index vorhanden.")
    
    elif args.command == "query":
        if not args.query:
            print("Bitte Suchbegriff angeben.", file=sys.stderr)
            sys.exit(1)
        
        hits = query_rag(args.query, CHROMA_DIR, args.results)
        
        if not hits:
            print("Keine Ergebnisse.")
        else:
            print(f"\n🔍 Ergebnisse für: \"{args.query}\"\n")
            for hit in hits:
                meta = hit["metadata"]
                source = meta.get("book_title", "?")
                chapter = meta.get("chapter_title", "?")
                print(f"#{hit['rank']} [{hit['score']:.2f}] {source} → {chapter}")
                print(f"   {hit['text'][:200]}{'...' if len(hit['text']) > 200 else ''}")
                print()

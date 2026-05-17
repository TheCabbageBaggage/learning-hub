/* data.js — Content loader and cache */

const Data = (() => {
  let _tracks = null;
  const _cache = {}; // cache for fetched book content: key = `${trackId}::${bookId}`

  /** Load tracks from the main tracks.json */
  async function _loadTracks() {
    if (_tracks) return _tracks;
    const res = await fetch('tracks.json');
    if (!res.ok) throw new Error('Failed to load tracks.json');
    _tracks = await res.json();
    return _tracks;
  }

  /** Get all tracks */
  async function getTracks() {
    return await _loadTracks();
  }

  /** Get a single track by ID */
  async function getTrack(trackId) {
    const tracks = await _loadTracks();
    return tracks.find(t => t.id === trackId) || null;
  }

  /** Get books for a track. If the track has inline chapters, return those.
   *  Otherwise, try to fetch from content/{trackId}/ directory. */
  async function getBooks(trackId) {
    const track = await getTrack(trackId);
    if (!track) return [];
    return track.books;
  }

  /** Get a specific book */
  async function getBook(trackId, bookId) {
    const books = await getBooks(trackId);
    return books.find(b => b.id === bookId) || null;
  }

  /** Get chapters for a book. This checks if the data is inline (from tracks.json)
   *  or needs to be fetched from a separate content directory. */
  async function getChapters(trackId, bookId) {
    const book = await getBook(trackId, bookId);
    if (!book) return [];

    // If chapters are inline, return them
    if (book.chapters && book.chapters.length > 0) {
      return book.chapters;
    }

    // If book has a source path, fetch from there
    if (book.source) {
      const cacheKey = `${trackId}::${bookId}`;
      if (_cache[cacheKey]) return _cache[cacheKey].chapters || [];
      try {
        const res = await fetch(book.source);
        if (res.ok) {
          const data = await res.json();
          _cache[cacheKey] = data;
          return data.chapters || [];
        }
      } catch { /* not available */ }
      return [];
    }

    // Legacy: try content directory
    const cacheKey = `${trackId}::${bookId}`;
    if (_cache[cacheKey]) return _cache[cacheKey].chapters || [];
    try {
      const res = await fetch(`content/${trackId}/${bookId}.json`);
      if (res.ok) {
        const data = await res.json();
        _cache[cacheKey] = data;
        return data.chapters || [];
      }
    } catch { /* not available */ }

    return [];
  }

  /** Get a single chapter by ID */
  async function getChapter(trackId, bookId, chapterId) {
    const chapters = await getChapters(trackId, bookId);
    return chapters.find(c => c.id === chapterId) || null;
  }

  /** Get flashcards for a chapter */
  async function getFlashcards(trackId, bookId, chapterId) {
    const chapter = await getChapter(trackId, bookId, chapterId);
    return chapter ? (chapter.flashcards || []) : [];
  }

  /** Get quiz questions for a chapter */
  async function getQuiz(trackId, bookId, chapterId) {
    const chapter = await getChapter(trackId, bookId, chapterId);
    return chapter ? (chapter.quiz || []) : [];
  }

  return { getTracks, getTrack, getBooks, getBook, getChapters, getChapter, getFlashcards, getQuiz };
})();

/* store.js — localStorage-based progress tracking */

const Store = (() => {
  const STORE_KEY = 'learning-hub-progress';
  const ACTIVITY_KEY = 'learning-hub-activity';

  function loadStore() {
    try {
      return JSON.parse(localStorage.getItem(STORE_KEY)) || {};
    } catch { return {}; }
  }

  function saveStore(data) {
    localStorage.setItem(STORE_KEY, JSON.stringify(data));
  }

  function loadActivity() {
    try {
      return JSON.parse(localStorage.getItem(ACTIVITY_KEY)) || {};
    } catch { return {}; }
  }

  function saveActivity(data) {
    localStorage.setItem(ACTIVITY_KEY, JSON.stringify(data));
  }

  function todayKey() {
    return new Date().toISOString().slice(0, 10);
  }

  function recordActivity() {
    const act = loadActivity();
    act[todayKey()] = (act[todayKey()] || 0) + 1;
    saveActivity(act);
  }

  /** Get progress for a specific (trackId, bookId) pair */
  function getProgress(trackId, bookId) {
    const store = loadStore();
    const key = `${trackId}::${bookId}`;
    return store[key] || { chapters: {}, quizzes: {}, flashcards: {} };
  }

  /** Update progress for a chapter activity
   *  type: 'flashcards_reviewed' | 'quiz_score' | 'chapter_complete'
   */
  function updateProgress(trackId, bookId, chapterId, type, score) {
    const store = loadStore();
    const key = `${trackId}::${bookId}`;
    if (!store[key]) {
      store[key] = { chapters: {}, quizzes: {}, flashcards: {} };
    }
    const progress = store[key];

    if (type === 'flashcards_reviewed') {
      if (!progress.flashcards[chapterId]) progress.flashcards[chapterId] = { reviewed: 0, gotIt: 0 };
      progress.flashcards[chapterId].reviewed += 1;
      if (score) progress.flashcards[chapterId].gotIt += 1;
    } else if (type === 'quiz_score') {
      if (!progress.quizzes[chapterId]) progress.quizzes[chapterId] = { attempts: 0, scores: [] };
      progress.quizzes[chapterId].attempts += 1;
      progress.quizzes[chapterId].scores.push(score);
    } else if (type === 'chapter_complete') {
      if (!progress.chapters[chapterId]) progress.chapters[chapterId] = {};
      progress.chapters[chapterId].completed = true;
      progress.chapters[chapterId].completedAt = new Date().toISOString();
    }

    saveStore(store);
    recordActivity();
  }

  /** Calculate streak: consecutive days with activity going back from today */
  function getStreak() {
    const act = loadActivity();
    const dates = Object.keys(act).sort().reverse();
    if (dates.length === 0) return 0;

    let streak = 0;
    const now = new Date();

    // Start from today and go backwards
    for (let i = 0; ; i++) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      const dk = d.toISOString().slice(0, 10);
      if (act[dk]) {
        streak++;
      } else {
        // Today might not have activity yet, skip one day
        if (i === 0) continue;
        break;
      }
    }
    return streak;
  }

  /** Get overall stats */
  function getStats() {
    const store = loadStore();
    const act = loadActivity();

    let totalChapters = 0;
    let totalQuizzes = 0;
    let quizScores = [];
    let totalFlashcards = 0;
    let flashcardsGot = 0;

    for (const key of Object.keys(store)) {
      const p = store[key];
      totalChapters += Object.values(p.chapters).filter(c => c.completed).length;
      for (const q of Object.values(p.quizzes)) {
        totalQuizzes += q.attempts;
        quizScores.push(...q.scores.map(s => s.score));
      }
      for (const f of Object.values(p.flashcards)) {
        totalFlashcards += f.reviewed;
        flashcardsGot += f.gotIt;
      }
    }

    return {
      chaptersCompleted: totalChapters,
      quizzesTaken: totalQuizzes,
      avgQuizScore: quizScores.length ? Math.round(quizScores.reduce((a,b) => a + b, 0) / quizScores.length) : 0,
      flashcardsReviewed: totalFlashcards,
      flashcardsRetention: totalFlashcards ? Math.round((flashcardsGot / totalFlashcards) * 100) : 0,
      streak: getStreak(),
      totalActivityDays: Object.keys(act).length,
    };
  }

  /** Get the chapter completion % for a (trackId, bookId) */
  function getChapterProgress(trackId, bookId, totalChapters) {
    const progress = getProgress(trackId, bookId);
    const completed = Object.values(progress.chapters).filter(c => c.completed).length;
    return totalChapters > 0 ? Math.round((completed / totalChapters) * 100) : 0;
  }

  /** Check if a specific chapter is done */
  function isChapterComplete(trackId, bookId, chapterId) {
    const progress = getProgress(trackId, bookId);
    return progress.chapters[chapterId]?.completed || false;
  }

  /** Get last activity for quick-resume */
  function getLastActivity() {
    const act = loadActivity();
    const store = loadStore();
    const dates = Object.keys(act).sort().reverse();
    if (dates.length === 0) return null;

    // Find most recently modified chapter
    let latestTime = null;
    let latestTrack = null;
    let latestBook = null;
    let latestChapter = null;

    for (const key of Object.keys(store)) {
      const [trackId, bookId] = key.split('::');
      const p = store[key];

      for (const [chId, ch] of Object.entries(p.chapters)) {
        if (ch.completedAt && (!latestTime || ch.completedAt > latestTime)) {
          latestTime = ch.completedAt;
          latestTrack = trackId;
          latestBook = bookId;
          latestChapter = chId;
        }
      }
    }

    if (latestTrack) {
      return { trackId: latestTrack, bookId: latestBook, chapterId: latestChapter };
    }
    return null;
  }

  /** Find next chapter to continue (first incomplete) */
  function getNextUp(tracks) {
    const last = getLastActivity();
    // If we have a last activity, find the next chapter after it, or the first incomplete
    for (const track of tracks) {
      for (const book of track.books) {
        const chapters = book.chapters;
        for (let i = 0; i < chapters.length; i++) {
          if (!isChapterComplete(track.id, book.id, chapters[i].id)) {
            return { trackId: track.id, bookId: book.id, chapterId: chapters[i].id, chapterTitle: chapters[i].title, bookTitle: book.title };
          }
        }
      }
    }
    return null;
  }

  return {
    getProgress,
    updateProgress,
    getStreak,
    getStats,
    getChapterProgress,
    isChapterComplete,
    getLastActivity,
    getNextUp,
    recordActivity,
    todayKey
  };
})();

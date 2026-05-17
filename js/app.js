/* app.js — Single-page router + all views (hash-based routing) */

const App = (() => {
  let fcState = null;
  let quizState = null;

  /* ─── Routing ─── */
  function init() {
    window.addEventListener('hashchange', renderRoute);
    document.addEventListener('keydown', handleKeyboard);
    if (!window.location.hash || window.location.hash === '#') window.location.hash = '#/';
    renderRoute();
  }

  function navigate(path) {
    window.location.hash = path;
  }

  function parseHash() {
    const raw = (window.location.hash || '#').replace(/^#\/?/, '');
    return raw ? raw.split('/').filter(Boolean) : [];
  }

  async function renderRoute() {
    const parts = parseHash();
    const main = document.getElementById('app-main');
    if (!main) return;

    if (parts[0] === 'stats') {
      renderStats(main);
    } else if (parts[0] === 'track' && parts.length >= 2) {
      const trackId = parts[1];
      if (parts[2] === 'book' && parts[4] === 'chapter') {
        await renderChapter(main, trackId, parts[3], parts[5]);
      } else {
        renderTrack(main, trackId);
      }
    } else {
      await renderDashboard(main);
    }
  }

  /* ─── Helpers ─── */
  function html(strings, ...vals) {
    let out = strings[0];
    for (let i = 0; i < vals.length; i++) out += String(vals[i]) + strings[i + 1];
    return out;
  }

  function $1(sel) { return document.querySelector(sel); }
  function $all(sel) { return document.querySelectorAll(sel); }

  function breadcrumb(...crumbs) {
    const links = [{ label: 'Home', href: '#/' }];
    crumbs.forEach(c => links.push(c));
    return links.map((c, i) =>
      i < links.length - 1
        ? `<a href="${c.href}">${c.label}</a><span class="sep">›</span>`
        : `<span class="current">${c.label}</span>`
    ).join('');
  }

  /* ─── Dashboard ─── */
  async function renderDashboard(container) {
    const tracks = await Data.getTracks();
    const stats = Store.getStats();
    const nextUp = Store.getNextUp(tracks);

    // Load chapter counts in parallel for all tracks/books
    const trackProgress = await Promise.all(tracks.map(async (t) => {
      let totalChapters = 0;
      let completedChapters = 0;
      const booksWithChapters = await Promise.all(t.books.map(async (b) => {
        const chapters = await Data.getChapters(t.id, b.id);
        totalChapters += chapters.length;
        completedChapters += chapters.filter(c => Store.isChapterComplete(t.id, b.id, c.id)).length;
        return { ...b, chapters };
      }));
      const pct = totalChapters > 0 ? Math.round((completedChapters / totalChapters) * 100) : 0;
      return { ...t, pct, totalChapters, completedChapters, booksWithChapters };
    }));

    const tracksHtml = trackProgress.map(t => {
      return html`
        <a class="track-card" href="#/track/${t.id}">
          <div class="track-icon">${t.icon}</div>
          <div class="track-title">${t.title}</div>
          <div class="track-desc">${t.description}</div>
          ${t.totalChapters > 0 ? html`
            <div class="progress-wrap">
              <div class="progress-label"><span>${t.pct}% complete (${t.completedChapters}/${t.totalChapters} chapters)</span></div>
              <div class="progress-bar"><div class="progress-fill" style="width:${t.pct}%"></div></div>
            </div>
          ` : `<div class="track-empty">Coming soon</div>`}
        </a>`;
    }).join('');

    const resumeHtml = nextUp ? html`
      <a class="quick-resume" href="#/track/${nextUp.trackId}/book/${nextUp.bookId}/chapter/${nextUp.chapterId}">
        <div class="qr-label">Continue Learning</div>
        <div class="qr-title">${nextUp.chapterTitle}</div>
        <div class="qr-sub">${nextUp.bookTitle}</div>
      </a>` : '';

    container.innerHTML = html`
      ${breadcrumb()}
      <div class="dashboard-header">
        <h1>📚 Learning Hub</h1>
        <p class="subtitle">Master skills with flashcards and quizzes. Track your progress daily.</p>
      </div>

      <div class="streak-bar">
        <div class="streak-card ${stats.streak > 0 ? 'fire' : ''}">
          <div class="icon">🔥</div>
          <div><div class="value">${stats.streak}</div><div class="label">Day Streak</div></div>
        </div>
        <div class="streak-card">
          <div class="icon">✅</div>
          <div><div class="value">${stats.chaptersCompleted}</div><div class="label">Chapters Done</div></div>
        </div>
        <div class="streak-card">
          <div class="icon">🧠</div>
          <div><div class="value">${stats.flashcardsReviewed}</div><div class="label">Cards Reviewed</div></div>
        </div>
        <div class="streak-card">
          <div class="icon">📝</div>
          <div><div class="value">${stats.quizzesTaken}</div><div class="label">Quizzes Taken</div></div>
        </div>
      </div>

      ${resumeHtml}

      <div class="track-grid">${tracksHtml}</div>
    `;
  }

  /* ─── Track View ─── */
  async function renderTrack(container, trackId) {
    const track = await Data.getTrack(trackId);
    if (!track) {
      container.innerHTML = '<div class="empty-state"><div class="icon">❌</div><p>Track not found</p></div>';
      return;
    }

    // Load all book chapter data in parallel
    const booksWithChapters = await Promise.all(track.books.map(async (book) => {
      const chapters = await Data.getChapters(trackId, book.id);
      return { ...book, chapters };
    }));

    const booksHtml = booksWithChapters.length === 0
      ? '<div class="empty-state"><div class="icon">📖</div><p>No books available yet</p></div>'
      : booksWithChapters.map(book => {
        const chapters = book.chapters || [];
        const total = chapters.length;
        const completed = chapters.filter(c => Store.isChapterComplete(trackId, book.id, c.id)).length;
        const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

        const chaptersHtml = chapters.map((ch, i) => {
          const done = Store.isChapterComplete(trackId, book.id, ch.id);
          return html`
            <a class="chapter-item ${done ? 'completed' : ''}" href="#/track/${trackId}/book/${book.id}/chapter/${ch.id}">
              <div class="ch-num">${done ? '✓' : i + 1}</div>
              <div class="ch-title">${ch.title}</div>
              ${done ? '<span class="ch-badge done">Done</span>' : ''}
            </a>`;
        }).join('');

        return html`
          <div class="book-card">
            <div class="book-title">${book.title}</div>
            <div class="book-author">by ${book.author || 'Unknown'}</div>
            ${total > 0 ? html`
              <div class="progress-label" style="margin-bottom:6px">
                <span>${completed}/${total} chapters</span><span>${pct}%</span>
              </div>
              <div class="progress-bar" style="margin-bottom:12px">
                <div class="progress-fill" style="width:${pct}%"></div>
              </div>
              <div class="chapter-list">${chaptersHtml}</div>
            ` : '<div style="color:var(--text-muted);font-size:0.85rem">No chapters yet</div>'}
          </div>`;
      }).join('');

    container.innerHTML = html`
      ${breadcrumb({ label: track.title, href: `#/track/${trackId}` })}
      <h1 style="font-size:1.6rem;font-weight:700;margin-bottom:4px">${track.icon} ${track.title}</h1>
      <p style="color:var(--text-secondary);margin-bottom:24px">${track.description}</p>
      ${booksHtml}
    `;
  }

  /* ─── Chapter View ─── */
  async function renderChapter(container, trackId, bookId, chapterId) {
    const book = await Data.getBook(trackId, bookId);
    const chapter = await Data.getChapter(trackId, bookId, chapterId);
    if (!book || !chapter) {
      container.innerHTML = '<div class="empty-state"><div class="icon">❌</div><p>Chapter not found</p></div>';
      return;
    }

    fcState = {
      trackId, bookId, chapterId,
      cards: chapter.flashcards || [],
      current: 0,
      reviewed: 0,
      gotIt: 0,
    };

    quizState = {
      trackId, bookId, chapterId,
      questions: chapter.quiz || [],
      answers: [],
      current: 0,
      submitted: false,
    };

    const flashcardCount = chapter.flashcards?.length || 0;
    const quizCount = chapter.quiz?.length || 0;
    const hasIntro = chapter.intro && chapter.intro.length > 0;

    container.innerHTML = html`
      ${breadcrumb(
        { label: book.title, href: `#/track/${trackId}/book/${bookId}` },
        { label: chapter.title }
      )}
      <button class="btn-back" id="nav-back-btn">← Back</button>
      <h1 style="font-size:1.4rem;font-weight:700;margin-bottom:4px">${chapter.title}</h1>
      <p style="color:var(--text-secondary);margin-bottom:20px">${book.title}</p>

      ${hasIntro ? html`
        <div class="chapter-intro" id="chapter-intro">
          <div class="intro-text">${chapter.intro}</div>
          ${chapter.images ? chapter.images.map(img => html`
            <figure class="intro-figure">
              <img src="${img.src}" alt="${img.alt || ''}" loading="lazy" />
              ${img.caption ? `<figcaption>${img.caption}</figcaption>` : ''}
            </figure>`).join('') : ''}
        </div>
      ` : ''}

      <div class="view-tabs">
        <button class="view-tab active" data-tab="flashcards" id="tab-btn-flashcards"
          ${flashcardCount === 0 ? 'disabled style="opacity:0.4"' : ''}>
          📇 Flashcards (${flashcardCount})
        </button>
        <button class="view-tab" data-tab="quiz" id="tab-btn-quiz"
          ${quizCount === 0 ? 'disabled style="opacity:0.4"' : ''}>
          📝 Quiz (${quizCount})
        </button>
      </div>

      <div id="tab-flashcards" class="tab-content">${renderFlashcards()}</div>
      <div id="tab-quiz" class="tab-content" style="display:none">${renderQuiz()}</div>
    `;

    $1('#nav-back-btn').addEventListener('click', () => navigateBack());
    $all('.view-tab:not([disabled])').forEach(tab => {
      tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
  }

  function switchTab(name) {
    $all('.view-tab').forEach(t => t.classList.remove('active'));
    $all('.tab-content').forEach(c => c.style.display = 'none');
    $1(`[data-tab="${name}"]`).classList.add('active');
    $1(`#tab-${name}`).style.display = 'block';
  }

  /* ─── Flashcard Rendering ─── */
  function renderFlashcards() {
    if (!fcState || fcState.cards.length === 0) {
      return '<div class="empty-state"><div class="icon">📇</div><p>No flashcards for this chapter yet</p></div>';
    }
    return html`
      <div class="flashcard-container">
        <div class="flashcard-counter">Card <span id="fc-count">${fcState.current + 1}</span> of ${fcState.cards.length}</div>

        <div class="flashcard" id="flashcard" onclick="App.flipCard()">
          <div class="flashcard-inner" id="fc-inner">
            <div class="flashcard-front">
              <div style="font-size:0.75rem;opacity:0.6;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:12px">Question</div>
              <div id="fc-front-text"></div>
            </div>
            <div class="flashcard-back">
              <div style="font-size:0.75rem;opacity:0.7;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:12px">Answer</div>
              <div id="fc-back-text"></div>
            </div>
          </div>
        </div>

        <div class="flashcard-actions" id="fc-actions">
          <button class="btn btn-flip" id="flip-btn" onclick="App.flipCard()">🔄 Flip</button>
          <button class="btn btn-ghost btn-sm" onclick="App.markGotIt(false)">↺ Review again</button>
          <button class="btn btn-success btn-sm" onclick="App.markGotIt(true)">✓ Got it</button>
        </div>
        <div id="fc-progress-wrap" style="width:100%;max-width:520px;margin-top:8px">
          <div class="progress-bar"><div class="progress-fill" id="fc-progress-fill" style="width:0%"></div></div>
        </div>
        <div id="fc-session-done" style="display:none;margin-top:16px;text-align:center;width:100%;max-width:520px">
          <div class="session-review">
            <div style="font-size:2rem;font-weight:800">${fcState.gotIt}/${fcState.cards.length}</div>
            <div style="color:var(--text-secondary);margin-top:4px">cards mastered this session</div>
            <div style="margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
              <button class="btn btn-primary" onclick="App.resetFlashcards()">🔄 Study again</button>
              <button class="btn btn-outline" onclick="App.markChapterDone()">✅ Mark chapter done</button>
            </div>
          </div>
        </div>
      </div>`;
  }

  function updateFlashcardDisplay() {
    if (!fcState || fcState.current >= fcState.cards.length) return;
    const card = fcState.cards[fcState.current];
    $1('#flashcard')?.classList.remove('flipped');
    $1('#fc-front-text').textContent = card.front;
    $1('#fc-back-text').textContent = card.back;
    $1('#fc-count').textContent = fcState.current + 1;
    const pct = Math.round(((fcState.current) / fcState.cards.length) * 100);
    const fill = $1('#fc-progress-fill');
    if (fill) fill.style.width = pct + '%';
  }

  /* ─── Quiz Rendering ─── */
  function renderQuiz() {
    if (!quizState || quizState.questions.length === 0) {
      return '<div class="empty-state"><div class="icon">📝</div><p>No quiz for this chapter yet</p></div>';
    }
    if (quizState.submitted) return renderQuizReview();

    const q = quizState.questions[quizState.current];
    const letters = ['A', 'B', 'C', 'D'];
    const answered = quizState.answers[quizState.current] !== undefined;

    return html`
      <div class="quiz-container">
        <div style="margin-bottom:16px;font-size:0.85rem;color:var(--text-secondary)">
          Question ${quizState.current + 1} of ${quizState.questions.length}
        </div>
        <div class="quiz-card" id="quiz-card">
          <div class="quiz-question">${q.question}</div>
          <div class="quiz-options" id="quiz-options">
            ${q.options.map((opt, i) => html`
              <button class="quiz-option" data-opt="${i}" onclick="App.selectQuizOption(${i})">
                <span class="opt-letter">${letters[i]}</span>
                <span>${opt}</span>
              </button>`).join('')}
          </div>
          <div id="quiz-feedback" style="display:none;margin-top:14px"></div>
        </div>
        ${answered ? html`
          <div style="display:flex;gap:10px;justify-content:flex-end">
            <button class="btn btn-primary" onclick="App.nextQuizQuestion()">
              ${quizState.current < quizState.questions.length - 1 ? 'Next →' : 'Finish Quiz →'}
            </button>
          </div>` : html`
          <div style="font-size:0.8rem;color:var(--text-muted);text-align:center;margin-top:8px">
            Press <kbd>1</kbd>-<kbd>4</kbd> to answer
          </div>`}
      </div>`;
  }

  function renderQuizReview() {
    const total = quizState.questions.length;
    const correct = quizState.answers.filter(a => a.correct).length;
    const score = Math.round((correct / total) * 100);
    const letters = ['A', 'B', 'C', 'D'];

    const rows = quizState.answers.map((a, i) => {
      const q = quizState.questions[i];
      return html`
        <div class="quiz-card ${a.correct ? 'correct' : 'wrong'}">
          <div class="quiz-question">${i + 1}. ${q.question}</div>
          <div class="quiz-options">
            ${q.options.map((opt, j) => html`
              <div class="quiz-option disabled ${j === q.correct ? 'correct-answer' : ''} ${j === a.selected && !a.correct ? 'wrong-answer' : ''}">
                <span class="opt-letter">${letters[j]}</span>
                <span>${opt}</span>
                ${j === q.correct ? ' ✓' : ''}
                ${j === a.selected && !a.correct ? ' ✗' : ''}
              </div>`).join('')}
          </div>
          <div class="quiz-explanation">${q.explanation}</div>
        </div>`;
    }).join('');

    return html`
      <div class="session-review">
        <div class="sr-score">${correct}/${total}</div>
        <div class="sr-total">${score}% — ${score >= 70 ? 'Great job! 🎉' : 'Keep practicing! 💪'}</div>
      </div>
      <div class="quiz-container" style="margin-top:20px">${rows}</div>
      <div style="max-width:640px;margin:20px auto;text-align:center">
        <button class="btn btn-primary" onclick="App.resetQuiz()">🔄 Retry Quiz</button>
        <button class="btn btn-outline" onclick="App.markChapterDone()">✅ Mark chapter done</button>
      </div>`;
  }

  /* ─── Stats View ─── */
  async function renderStats(container) {
    const tracks = await Data.getTracks();
    const stats = Store.getStats();

    const trackRows = tracks.map(t => {
      let totalCh = 0, completedCh = 0, qTotal = 0, qPass = 0;

      for (const book of t.books) {
        const chCount = book.chapters?.length || 0;
        totalCh += chCount;
        completedCh += book.chapters?.filter(c => Store.isChapterComplete(t.id, book.id, c.id)).length || 0;
        const p = Store.getProgress(t.id, book.id);
        for (const [, q] of Object.entries(p.quizzes)) {
          qTotal += q.scores.length;
          qPass += q.scores.filter(s => s.score >= 70).length;
        }
      }

      const pct = totalCh > 0 ? Math.round((completedCh / totalCh) * 100) : 0;
      return html`
        <tr>
          <td>${t.icon} ${t.title}</td>
          <td>${completedCh}/${totalCh}</td>
          <td><div class="progress-bar" style="margin:4px 0"><div class="progress-fill" style="width:${pct}%"></div></div>${pct}%</td>
          <td>${qTotal}</td>
          <td>${qTotal > 0 ? Math.round((qPass / qTotal) * 100) + '%' : '—'}</td>
        </tr>`;
    }).join('');

    container.innerHTML = html`
      ${breadcrumb({ label: '📊 Statistics', href: '#/stats' })}
      <h1 style="font-size:1.6rem;font-weight:700;margin-bottom:24px">Your Progress</h1>

      <div class="stats-grid">
        <div class="stat-card primary"><div class="stat-value">🔥 ${stats.streak}</div><div class="stat-label">Day Streak</div></div>
        <div class="stat-card"><div class="stat-value">✅ ${stats.chaptersCompleted}</div><div class="stat-label">Chapters Completed</div></div>
        <div class="stat-card"><div class="stat-value">🧠 ${stats.flashcardsReviewed}</div><div class="stat-label">Cards Reviewed</div></div>
        <div class="stat-card"><div class="stat-value">📝 ${stats.quizzesTaken}</div><div class="stat-label">Quizzes Taken</div></div>
        <div class="stat-card"><div class="stat-value">${stats.avgQuizScore}%</div><div class="stat-label">Avg Quiz Score</div></div>
        <div class="stat-card"><div class="stat-value">${stats.flashcardsRetention}%</div><div class="stat-label">Card Retention</div></div>
      </div>

      <div style="overflow-x:auto">
        <table class="track-stats-table">
          <thead><tr><th>Track</th><th>Chapters</th><th>Progress</th><th>Quizzes Taken</th><th>Pass Rate</th></tr></thead>
          <tbody>
            ${trackRows || '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">No data yet</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
  }

  /* ─── Keyboard Shortcuts ─── */
  function handleKeyboard(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (fcState) {
      if (e.key === ' ') { e.preventDefault(); flipCard(); }
      if (e.key === 'ArrowRight') { e.preventDefault(); nextFlashcard(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); prevFlashcard(); }
    }

    if (quizState && !quizState.submitted) {
      const keyMap = { '1': 0, '2': 1, '3': 2, '4': 3 };
      if (keyMap[e.key] !== undefined) selectQuizOption(keyMap[e.key]);
      if (e.key === 'Enter') {
        const answered = quizState.answers[quizState.current] !== undefined;
        if (answered) nextQuizQuestion();
      }
    }

    if (e.key === 'Escape') {
      navigateBack();
    }
  }

  /* ─── Flashcard Actions ─── */
  function flipCard() {
    const el = $1('#flashcard');
    if (!el || !fcState) return;
    el.classList.toggle('flipped');
  }

  function markGotIt(gotIt) {
    if (!fcState) return;
    Store.updateProgress(fcState.trackId, fcState.bookId, fcState.chapterId, 'flashcards_reviewed', gotIt);
    fcState.reviewed++;
    if (gotIt) fcState.gotIt++;

    if (fcState.current < fcState.cards.length - 1) {
      fcState.current++;
      $1('#flashcard')?.classList.remove('flipped');
      updateFlashcardDisplay();
    } else {
      // Session done — show summary
      const pct = Math.round((fcState.gotIt / fcState.cards.length) * 100);
      $1('#fc-progress-fill').style.width = '100%';
      $1('#fc-actions').style.display = 'none';
      $1('.flashcard-counter').style.display = 'none';
      $1('.flashcard-hint').style.display = 'none';
      $1('#fc-progress-wrap').style.display = 'none';
      $1('#fc-session-done').style.display = 'block';
    }
  }

  function nextFlashcard() {
    if (!fcState || fcState.current >= fcState.cards.length - 1) return;
    fcState.current++;
    $1('#flashcard')?.classList.remove('flipped');
    updateFlashcardDisplay();
  }

  function prevFlashcard() {
    if (!fcState || fcState.current <= 0) return;
    fcState.current--;
    $1('#flashcard')?.classList.remove('flipped');
    updateFlashcardDisplay();
  }

  function resetFlashcards() {
    if (!fcState) return;
    fcState.current = 0;
    fcState.reviewed = 0;
    fcState.gotIt = 0;
    $1('#flashcard')?.classList.remove('flipped');
    $1('#fc-actions').style.display = 'flex';
    $1('.flashcard-counter').style.display = 'block';
    $1('.flashcard-hint').style.display = 'block';
    $1('#fc-progress-wrap').style.display = 'block';
    $1('#fc-session-done').style.display = 'none';
    $1('#fc-progress-fill').style.width = '0%';
    updateFlashcardDisplay();
  }

  /* ─── Quiz Actions ─── */
  function selectQuizOption(idx) {
    if (!quizState || quizState.submitted) return;
    if (quizState.answers[quizState.current] !== undefined) return;

    const q = quizState.questions[quizState.current];
    const correct = idx === q.correct;
    quizState.answers[quizState.current] = { selected: idx, correct };

    Store.updateProgress(quizState.trackId, quizState.bookId, quizState.chapterId, 'quiz_score', correct ? 100 : 0);

    // Update option styles
    $all('.quiz-option').forEach(o => {
      o.classList.add('disabled');
      const optIdx = parseInt(o.dataset.opt);
      if (optIdx === q.correct) o.classList.add('correct-answer');
      if (optIdx === idx && !correct) o.classList.add('wrong-answer');
    });

    const feedback = $1('#quiz-feedback');
    if (feedback) {
      feedback.style.display = 'block';
      feedback.innerHTML = correct
        ? `<span style="color:var(--success)">✓ Correct!</span>`
        : `<span style="color:var(--danger)">✗ Wrong! Correct answer: ${q.options[q.correct]}</span>`;
    }

    // Show next button
    const card = $1('.quiz-card');
    if (card) {
      const nextBtn = document.createElement('div');
      nextBtn.style.cssText = 'display:flex;gap:10px;justify-content:flex-end;margin-top:14px';
      nextBtn.innerHTML = `<button class="btn btn-primary" onclick="App.nextQuizQuestion()">
        ${quizState.current < quizState.questions.length - 1 ? 'Next →' : 'Finish Quiz →'}
      </button>`;
      card.appendChild(nextBtn);
    }
  }

  function nextQuizQuestion() {
    if (!quizState) return;
    if (quizState.current < quizState.questions.length - 1) {
      quizState.current++;
      $1('#tab-quiz').innerHTML = renderQuiz();
    } else {
      quizState.submitted = true;
      $1('#tab-quiz').innerHTML = renderQuizReview();
    }
  }

  function resetQuiz() {
    if (!quizState) return;
    quizState.answers = [];
    quizState.current = 0;
    quizState.submitted = false;
    $1('#tab-quiz').innerHTML = renderQuiz();
  }

  /* ─── Chapter done ─── */
  function markChapterDone() {
    const trackId = fcState?.trackId || quizState?.trackId;
    const bookId = fcState?.bookId || quizState?.bookId;
    const chapterId = fcState?.chapterId || quizState?.chapterId;
    if (!trackId) return;
    Store.updateProgress(trackId, bookId, chapterId, 'chapter_complete');
    navigate(`#/track/${trackId}/book/${bookId}`);
  }

  /* ─── Navigate back ─── */
  function navigateBack() {
    const parts = parseHash();
    if (parts[2] === 'book') {
      navigate(`#/track/${parts[1]}`);
    } else {
      navigate('#/');
    }
  }

  /* ─── Public API ─── */
  return {
    init,
    navigate,
    navigateBack,
    flipCard,
    markGotIt,
    resetFlashcards,
    nextFlashcard,
    prevFlashcard,
    selectQuizOption,
    nextQuizQuestion,
    resetQuiz,
    markChapterDone,
  };
})();

document.addEventListener('DOMContentLoaded', () => App.init());
/* Lesson player: một hoạt động một màn hình. Người học 10 phút không cuộn. */
const Player = (() => {
  let L = null, flat = [], idx = 0, busy = false;
  function init(data) {
    L = data; flat = [];
    data.activities.forEach(a => a.items.forEach(i => flat.push({ ...i, act: a.kind })));
    // Chèn màn "Học từ & hội thoại" làm bước ĐẦU TIÊN nếu bài có nội dung học.
    const s = data.study || {};
    L.hasStudy = (s.vocabulary && s.vocabulary.length) ||
      (s.dialogue && s.dialogue.turns && s.dialogue.turns.length) ||
      (s.sentence_patterns && s.sentence_patterns.length);
    if (L.hasStudy) flat.unshift({ __study: true });
    if (!flat.length) { document.getElementById('stage').innerHTML = '<div class="empty">Bài này chưa có nội dung.</div>'; return; }
    render();
  }
  // Nhãn kỹ năng cho từng bước — để người học luôn biết đang luyện gì.
  function stepMeta(it) {
    if (it.__study) return { icon: '📖', label: 'Học từ & hội thoại' };
    if (it.choices && it.choices.length) {
      if (it.audio) return { icon: '🎧', label: 'Nghe hiểu' };
      return L.phase === 'reading'
        ? { icon: '📖', label: 'Đọc hiểu' }
        : { icon: '🧠', label: 'Ôn từ & mẫu câu' };
    }
    return { icon: '🎙', label: it.act === 'shadow' ? 'Nói — nhắc lại mẫu' : 'Nói' };
  }
  function steps() {
    return flat.map((it, i) => {
      const m = stepMeta(it);
      return `<i class="${i < idx ? 'done' : i === idx ? 'now' : ''}" title="${esc(m.label)}"></i>`;
    }).join('');
  }
  function render() {
    const it = flat[idx];
    const m = stepMeta(it);
    document.getElementById('steps').innerHTML = steps();
    document.getElementById('counter').textContent = `Bước ${idx + 1}/${flat.length} · ${m.icon} ${m.label}`;
    const nb = document.getElementById('nextBtn');
    if (it.__study) {
      document.getElementById('stage').innerHTML = studyView();
      nb.disabled = false;                       // màn học: không chấm, cho đi tiếp ngay
      nb.textContent = 'Bắt đầu luyện tập';
      return;
    }
    document.getElementById('stage').innerHTML = (it.choices && it.choices.length) ? quizView(it) : speakView(it);
    nb.disabled = true;
    nb.textContent = idx === flat.length - 1 ? 'Hoàn thành' : 'Tiếp theo';
  }

  function studyView() {
    const s = L.study || {}, vocab = s.vocabulary || [], dlg = s.dialogue || {}, pats = s.sentence_patterns || [];
    const play = (a) => a ? `<button class="playbtn" onclick="Player.play('${a}')"><svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button>` : '';
    const topic = s.topic || 'core';
    let h = '<div class="card">'
      + `<img src="/static/img/topic-${topic}.svg" alt="" width="56" height="56" style="display:block;margin:0 auto .4rem">`
      + '<div class="center" style="margin-bottom:.9rem"><span class="pill pill-acc">📖 Học từ &amp; hội thoại</span></div>';
    if (vocab.length) {
      h += '<h3 style="margin:.4rem 0 .5rem">Từ vựng</h3>';
      vocab.forEach(v => {
        h += `<div class="vrow"><div class="between" style="gap:.5rem">
          <div><b>${esc(v.term)}</b> <span class="mut-3">${esc(v.ipa || '')}</span></div>${play(v.audio)}</div>
          <div class="mut-3">${esc(v.meaning_vi || '')}</div>
          ${v.chunk ? `<div style="font-size:.88rem;margin-top:.15rem">“${esc(v.chunk)}”</div>` : ''}</div>`;
      });
    }
    if (dlg.turns && dlg.turns.length) {
      h += '<h3 style="margin:1.1rem 0 .3rem">Hội thoại</h3>';
      if (dlg.context_vi) h += `<div class="mut-3" style="margin-bottom:.6rem">${esc(dlg.context_vi)}</div>`;
      dlg.turns.forEach(t => {
        h += `<div class="dturn"><div class="between" style="gap:.5rem">
          <div><span class="spk">${esc(t.speaker || '')}</span> <b>${esc(t.en)}</b></div>${play(t.audio)}</div>
          <div class="mut-3">${esc(t.vi || '')}</div></div>`;
      });
    }
    if (pats.length) {
      h += '<h3 style="margin:1.1rem 0 .3rem">Mẫu câu</h3>';
      pats.forEach(p => { h += `<div class="dturn"><b>${esc(p.pattern)}</b><div class="mut-3">${esc(p.meaning_vi || '')}</div></div>`; });
    }
    h += '<p class="hint" style="margin-top:1rem">Đọc và nghe qua một lượt, rồi bấm “Bắt đầu luyện tập”.</p></div>';
    return h;
  }
  function quizView(it) {
    const m = stepMeta(it);
    return `<div class="card">
      <div class="pill pill-acc" style="margin-bottom:.9rem">${m.icon} ${esc(m.label)}</div>
      ${it.audio ? `<button class="playbtn" onclick="Player.play('${it.audio}')"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Nghe câu</button>` : ''}
      <p class="prompt-vi" style="margin:.9rem 0 1rem;font-size:.98rem;color:var(--fg)">${esc(it.prompt_vi || it.prompt_en)}</p>
      <div id="choices">${it.choices.map((c, i) => `<button class="choice" data-i="${i}" onclick="Player.answer(${i})">${esc(c)}</button>`).join('')}</div>
      <div id="fb" style="margin-top:.9rem"></div></div>`;
  }
  function speakView(it) {
    const m = stepMeta(it);
    return `<div class="card center">
      <div class="pill pill-acc" style="margin-bottom:.9rem">${m.icon} ${esc(m.label)}</div>
      <p class="prompt-en">${esc(it.prompt_en || '')}</p>
      ${it.ipa ? `<div class="prompt-ipa">${esc(it.ipa)}</div>` : ''}
      ${it.prompt_vi ? `<p class="prompt-vi">${esc(it.prompt_vi)}</p>` : ''}
      ${it.audio ? `<button class="playbtn" style="margin:1rem 0" onclick="Player.play('${it.audio}')"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Nghe giọng mẫu</button>` : ''}
      <div style="margin:1.4rem 0 .6rem"><button class="mic" id="mic" onclick="Player.mic()" aria-label="Ghi âm">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3"/></svg></button></div>
      <div class="mut-3" id="micHint">Bấm để ghi âm, bấm lần nữa để dừng</div>
      <div id="result"></div></div>`;
  }
  function play(src) { new Audio(src).play().catch(() => toast('Không phát được audio (chưa sinh file). Chạy make seed.', 'warn')); }
  async function answer(i) {
    if (busy) return; busy = true;
    document.querySelectorAll('.choice').forEach(b => b.disabled = true);
    const it = flat[idx];
    const r = await api('/api/v1/learn/attempt', { item_id: it.id, choice_index: i, latency_ms: 0, is_preview: L.is_preview });
    busy = false;
    if (!r.ok) { toast(r.data.detail || 'Lỗi khi chấm bài.', 'err'); return; }
    document.querySelectorAll('.choice')[i].classList.add(r.data.is_correct ? 'ok' : 'no');
    document.getElementById('fb').innerHTML = `<div class="alert alert-${r.data.is_correct ? 'ok' : 'warn'}">${esc(r.data.feedback_vi)}</div>`;
    done(r.data);
  }
  async function mic() {
    const btn = document.getElementById('mic'), hint = document.getElementById('micHint');
    if (btn.classList.contains('rec')) {
      btn.classList.remove('rec'); btn.disabled = true; hint.textContent = 'Đang chấm…';
      const blob = await Recorder.stop(); await upload(blob);
      btn.disabled = false; hint.textContent = 'Bấm để thử lại'; return;
    }
    try { await Recorder.start(); btn.classList.add('rec'); hint.textContent = 'Đang nghe… bấm lần nữa để dừng'; }
    catch (e) { toast(e.message, 'err'); }
  }
  async function upload(blob) {
    if (!blob || blob.size < 800) { toast('Chưa nghe được gì. Bạn nói to hơn nhé.', 'warn'); return; }
    const it = flat[idx];
    const fd = new FormData();
    fd.append('audio', blob, 'a.webm'); fd.append('item_id', it.id); fd.append('is_preview', L.is_preview ? 'true' : 'false');
    const r = await fetch('/api/v1/speech/attempt', { method: 'POST', body: fd });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { toast(j.detail || 'Chưa chấm được. Thử lại nhé.', 'err'); return; }
    showScores(j); done(j);
  }
  function band(v) { return v >= 75 ? 'Tốt' : v >= 50 ? 'Khá' : 'Cần luyện'; }
  function showScores(j) {
    const words = (j.phoneme_diff && j.phoneme_diff.words) || [];
    document.getElementById('result').innerHTML = `
      <div class="scores">
        <div class="score"><div class="v">${band(j.score_pronunciation)}</div><div class="k">Phát âm</div></div>
        <div class="score"><div class="v">${band(j.score_fluency)}</div><div class="k">Trôi chảy</div></div>
        <div class="score"><div class="v">${band(j.score_communication)}</div><div class="k">Giao tiếp</div></div></div>
      ${words.length ? `<div class="words">${words.map(w => `<span class="${w.score >= 75 ? '' : w.score >= 50 ? 'mid' : 'bad'}">${esc(w.word)}</span>`).join('')}</div>` : ''}
      ${j.transcript ? `<div class="mut-3" style="margin:.4rem 0 .8rem">Mình nghe được: “${esc(j.transcript)}”</div>` : ''}
      <div class="alert alert-info" style="text-align:left">${esc(j.feedback_vi)}</div>`;
  }
  function done(d) {
    document.getElementById('nextBtn').disabled = false;
    if (d.mastery_raw !== undefined && !L.is_preview) {
      const bar = document.getElementById('mbar'); if (bar) bar.style.width = Math.min(100, d.mastery_raw) + '%';
      const lbl = document.getElementById('mval'); if (lbl) lbl.textContent = Math.round(d.mastery_raw) + '%';
    }
    if (d.unlocked_codes && d.unlocked_codes.length) toast(`Đã mở ${d.unlocked_codes.length} bài mới`, 'ok');
  }
  function next() { if (idx < flat.length - 1) { idx++; render(); window.scrollTo(0, 0); } else finish(); }
  async function finish() {
    Recorder.release();
    if (L.is_preview) { location.href = '/learn'; return; }
    const r = await api('/api/v1/learn/next'); const n = r.data || {};
    document.getElementById('stage').innerHTML = `<div class="card center"><div style="font-size:2.4rem;margin-bottom:.6rem">✅</div>
      <h2>Xong bài rồi</h2><p class="mut" style="margin:.5rem 0 1.4rem">Bạn vừa hoàn thành ${flat.filter(x => !x.__study).length} hoạt động.</p>
      <div class="card-tight" style="background:var(--card-2);text-align:left;margin-bottom:1.2rem;border-radius:var(--r)">
        <div class="hero-tag">Gợi ý tiếp theo</div><div style="font-weight:600;margin:.35rem 0">${esc(n.title_vi || 'Ôn tập')}</div>
        <div class="mut-3" style="line-height:1.6">${esc(n.reason_vi || '')}</div></div>
      <a class="btn btn-lg btn-full" href="${n.code ? '/learn/lesson/' + n.code : '/learn'}">Học tiếp</a>
      <a class="btn btn-quiet btn-full" style="margin-top:.5rem" href="/learn">Về lộ trình</a></div>`;
    document.getElementById('steps').innerHTML = flat.map(() => '<i class="done"></i>').join('');
    document.querySelector('.player-nav').style.display = 'none';
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  return { init, play, answer, mic, next };
})();

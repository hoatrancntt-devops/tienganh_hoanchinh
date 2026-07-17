/* Placement runner. Đáp án không bao giờ ở phía client — server lột trước khi trả form. */
const Placement = (() => {
  let form = null, testId = null, i = 0, answers = [], plays = 0, t0 = 0;
  const SECTION_VI = { self: 'Tự đánh giá', vocab: 'Từ vựng', grammar: 'Ngữ pháp', listening: 'Nghe', speaking: 'Nói' };
  async function start() {
    const f = await api('/api/v1/placement/form/A');
    if (!f.ok) { toast('Không tải được đề.', 'err'); return; }
    const s = await api('/api/v1/placement/start?form=A', {});
    if (!s.ok) { toast(s.data.detail || 'Không bắt đầu được.', 'err'); return; }
    form = f.data; testId = s.data.test_id; i = 0; answers = [];
    document.getElementById('intro').hidden = true; document.getElementById('test').hidden = false; render();
  }
  function render() {
    const it = form.items[i]; plays = 0; t0 = Date.now();
    document.getElementById('pSteps').innerHTML = form.items.map((_, k) => `<i class="${k < i ? 'done' : k === i ? 'now' : ''}"></i>`).join('');
    document.getElementById('pSection').textContent = SECTION_VI[it.section] || it.section;
    document.getElementById('pCount').textContent = `${i + 1}/${form.items.length}`;
    const st = document.getElementById('pStage');
    if (it.section === 'self') st.innerHTML = likert(it);
    else if (it.section === 'speaking') st.innerHTML = speak(it);
    else st.innerHTML = mcq(it);
    window.scrollTo(0, 0);
  }
  function likert(it) { return `<div class="card"><p style="font-size:1.02rem;margin-bottom:1.1rem">${esc(it.prompt_vi)}</p><div class="likert">${it.choices.map((c, k) => `<button onclick="Placement.pick(${k})">${esc(c)}</button>`).join('')}</div><p class="hint" style="margin-top:.9rem">Câu này không tính điểm. Trả lời thật giúp hệ thống hiểu bạn hơn.</p></div>`; }
  function mcq(it) {
    const audio = it.section === 'listening';
    return `<div class="card">${audio ? `<div class="center" style="margin-bottom:1.1rem"><button class="playbtn" id="pl" onclick="Placement.playIt('${it.id}')"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Nghe</button><div class="mut-3" id="plc" style="margin-top:.5rem">Nghe lại tối đa 2 lần</div></div>` : ''}
      <p style="font-size:1rem;margin-bottom:1rem">${esc(it.prompt_vi)}</p>${it.choices.map((c, k) => `<button class="choice" onclick="Placement.pick(${k})">${esc(c)}</button>`).join('')}</div>`;
  }
  function speak(it) {
    return `<div class="card center"><p class="prompt-vi" style="margin-bottom:.8rem">${esc(it.prompt_vi)}</p>
      ${it.kind !== 'repeat' && it.prompt_en !== undefined ? `<p class="prompt-en">${esc(it.prompt_en || '')}</p>` : ''}
      ${it.kind === 'repeat' ? `<button class="playbtn" onclick="Placement.playIt('${it.id}')" style="margin:.6rem 0 0"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Nghe câu</button>` : ''}
      <div style="margin:1.6rem 0 .5rem"><button class="mic" id="pmic" onclick="Placement.mic()" aria-label="Ghi âm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3"/></svg></button></div>
      <div class="mut-3" id="pmh">Bấm để ghi âm, bấm lần nữa để dừng</div>
      <button class="btn btn-quiet" style="margin-top:1rem" onclick="Placement.skip()">Bỏ qua câu này</button></div>`;
  }
  function playIt(id) {
    if (plays >= 2) { toast('Bạn đã nghe 2 lần rồi.', 'warn'); return; }
    plays++; const c = document.getElementById('plc'); if (c) c.textContent = plays >= 2 ? 'Đã hết lượt nghe lại' : 'Còn 1 lần nghe lại';
    new Audio(`/media/placement/${id}.wav`).play().catch(() => toast('Chưa có audio cho câu này (chạy make seed).', 'warn'));
  }
  function pick(k) { const it = form.items[i]; answers.push({ item_ref: it.id, section: it.section, kind: it.kind, choice_index: k, latency_ms: Date.now() - t0, replay_count: plays }); advance(); }
  function skip() { const it = form.items[i]; answers.push({ item_ref: it.id, section: it.section, kind: it.kind, latency_ms: 0 }); advance(); }
  async function mic() {
    const b = document.getElementById('pmic'), h = document.getElementById('pmh');
    if (b.classList.contains('rec')) {
      b.classList.remove('rec'); b.disabled = true; h.textContent = 'Đang xử lý…';
      const blob = await Recorder.stop(); const it = form.items[i];
      if (blob && blob.size > 800) {
        const fd = new FormData(); fd.append('audio', blob, 'a.webm'); fd.append('test_id', testId); fd.append('item_ref', it.id);
        const r = await fetch('/api/v1/speech/placement', { method: 'POST', body: fd });
        if (!r.ok) toast('Chưa chấm được câu này, hệ thống sẽ bỏ qua.', 'warn');
      }
      answers.push({ item_ref: it.id, section: it.section, kind: it.kind, audio_ref: it.id, latency_ms: Date.now() - t0 }); advance(); return;
    }
    try { await Recorder.start(); b.classList.add('rec'); h.textContent = 'Đang nghe… bấm lần nữa để dừng'; }
    catch (e) { toast(e.message, 'err'); }
  }
  function advance() { if (i < form.items.length - 1) { i++; render(); } else submit(); }
  async function submit() {
    Recorder.release();
    document.getElementById('test').hidden = true; document.getElementById('grading').hidden = false;
    const r = await api('/api/v1/placement/submit', { test_id: testId, responses: answers });
    if (!r.ok) { toast(r.data.detail || 'Chấm bài lỗi.', 'err'); return; }
    location.href = '/placement/result';
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  return { start, pick, skip, mic, playIt };
})();

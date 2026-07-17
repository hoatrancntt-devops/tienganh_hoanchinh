/* Ghi âm trình duyệt. Chuẩn hoá về WAV 16k mono là việc của server (ffmpeg). */
const Recorder = (() => {
  let stream = null, rec = null, chunks = [];
  function pickMime() {
    const list = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'];
    for (const m of list) if (window.MediaRecorder && MediaRecorder.isTypeSupported(m)) return m;
    return '';
  }
  async function ensure() {
    if (stream) return true;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)
      throw new Error('Trình duyệt không hỗ trợ ghi âm. Bạn thử Chrome hoặc Safari mới nhé.');
    if (!window.isSecureContext)
      throw new Error('Ghi âm cần HTTPS. Trên máy chủ thật bạn phải bật HTTPS.');
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 } });
    } catch (e) {
      if (e.name === 'NotAllowedError') throw new Error('Bạn chưa cho phép dùng micro. Bấm vào biểu tượng khoá trên thanh địa chỉ để bật.');
      throw new Error('Không mở được micro: ' + e.message);
    }
    return true;
  }
  async function start() {
    await ensure(); chunks = [];
    const mime = pickMime();
    rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
    rec.start();
  }
  function stop() {
    return new Promise((resolve) => {
      if (!rec || rec.state === 'inactive') return resolve(null);
      rec.onstop = () => resolve(new Blob(chunks, { type: rec.mimeType || 'audio/webm' }));
      rec.stop();
    });
  }
  function release() { if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; } }
  async function check() {
    try { await ensure(); return { ok: true }; } catch (e) { return { ok: false, error: e.message }; }
  }
  return { start, stop, release, check };
})();

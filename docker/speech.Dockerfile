# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Piper cần espeak-ng cho phoneme; ffmpeg để đọc audio đầu vào.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates tar espeak-ng ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        "fastapi==0.115.6" "uvicorn[standard]==0.34.0" \
        "faster-whisper==1.1.0" "python-multipart==0.0.20" "pydantic==2.10.4"

# Piper binary + 2 giọng. ~70MB tổng — chấp nhận được để có TTS offline miễn phí.
ARG PIPER_VER=2023.11.14-2
RUN mkdir -p /opt/piper/voices && cd /opt \
    && curl -fsSL -o piper.tgz \
       "https://github.com/rhasspy/piper/releases/download/${PIPER_VER}/piper_linux_x86_64.tar.gz" \
    && tar -xzf piper.tgz && rm piper.tgz \
    && for v in en_US-amy-medium en_US-ryan-medium; do \
         d=$(echo $v | cut -d- -f2); \
         curl -fsSL -o /opt/piper/voices/$v.onnx \
           "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/$d/medium/$v.onnx"; \
         curl -fsSL -o /opt/piper/voices/$v.onnx.json \
           "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/$d/medium/$v.onnx.json"; \
       done
ENV PATH="/opt/piper:$PATH" PIPER_VOICES_DIR=/opt/piper/voices

RUN useradd --create-home --uid 1001 speech
WORKDIR /srv
COPY --chown=speech:speech speech_service ./speech_service

RUN mkdir -p /srv/models && chown speech:speech /srv/models
ENV HF_HOME=/srv/models XDG_CACHE_HOME=/srv/models \
    PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2

USER speech
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8080/health || exit 1

CMD ["uvicorn", "speech_service.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]

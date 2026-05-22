# YouTube 쇼츠 파이프라인 실행 환경 (재현 가능한 컨테이너)
# 어느 PC에서든: git clone → .env 작성 → docker compose run 으로 동일 실행.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1) 시스템 의존성: ffmpeg + 한글폰트 + Remotion(헤드리스 Chromium) 런타임 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common curl ca-certificates gnupg git build-essential \
    ffmpeg fonts-nanum fontconfig \
    libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libgbm1 libasound2 \
    libxrandr2 libxkbcommon0 libxfixes3 libxcomposite1 libxdamage1 \
    libpango-1.0-0 libcairo2 libcups2 \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

# 2) Python 3.11 (deadsnakes) + Node 20 (NodeSource)
RUN add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
       python3.11 python3.11-venv python3.11-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3) Python 의존성 (변경 적은 레이어 먼저 → 캐시 활용)
COPY requirements.txt ./
RUN python3.11 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

# 4) Node/Remotion 의존성 + 헤드리스 브라우저 사전 다운로드(런타임 다운로드 제거)
COPY package.json package-lock.json ./
RUN npm ci --no-fund --no-audit \
    && npx remotion browser ensure

# 5) 앱 소스
COPY . .

# `docker compose run shorts "주제" --no-upload` 처럼 인자가 main.py로 전달됨
ENTRYPOINT ["python", "-m", "pipeline.main"]

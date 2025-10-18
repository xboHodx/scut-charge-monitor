FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /work

RUN apt-get update && \
    apt-get install -y git ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    git clone https://github.com/c-w-xiaohei/scut-charge-monitor.git && \
    rm -rf scut-charge-monitor/.git

WORKDIR /work/scut-charge-monitor

RUN uv sync
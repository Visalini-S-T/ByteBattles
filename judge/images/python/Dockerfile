FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
    time \
    coreutils \
    ca-certificates

RUN adduser -D -u 1000 run && \
    mkdir -p /workspace && \
    chown -R run:run /workspace

WORKDIR /workspace
USER run

CMD ["sleep", "infinity"]
FROM node:22-alpine

RUN apk add --no-cache \
    time \
    coreutils \
    ca-certificates

RUN adduser -D run && \
    mkdir -p /workspace && \
    chown -R run:run /workspace

WORKDIR /workspace
USER run

CMD ["sleep", "infinity"]

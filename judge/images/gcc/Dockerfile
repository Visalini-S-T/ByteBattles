FROM judge-python

USER root

RUN apk add --no-cache \
    gcc \
    g++ \
    make \
    libc-dev

WORKDIR /workspace

RUN chown -R run:run /workspace

USER run

CMD ["sleep", "infinity"]
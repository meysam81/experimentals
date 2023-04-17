FROM rust:1 AS builder

WORKDIR /usr/src/myapp
COPY . .

RUN cargo install --path .

FROM scratch AS runner

COPY --from=builder /usr/local/cargo/bin/fibo /usr/local/bin/fibo

ENTRYPOINT ["fibo"]

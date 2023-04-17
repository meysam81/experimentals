FROM rust:1.67-alpine as builder
WORKDIR /opt/helloworld
COPY . .
RUN cargo build --release

FROM scratch
COPY --from=builder /opt/helloworld/target/release/helloworld /opt/helloworld/helloworld
ENTRYPOINT ["/opt/helloworld/helloworld"]


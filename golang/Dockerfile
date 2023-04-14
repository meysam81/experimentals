FROM golang:1.20-alpine AS builder

WORKDIR /opt/app

COPY . .

RUN CGO_ENABLED=0 go build -o helloworld
RUN chmod +x helloworld

FROM scratch

COPY --from=builder /opt/app/helloworld /opt/app/helloworld

ENTRYPOINT ["/opt/app/helloworld"]

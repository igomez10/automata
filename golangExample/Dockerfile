FROM golang:1.13 as builder

WORKDIR /app

COPY src .
COPY go.mod .

RUN go mod download
ENV CGO_ENABLED 0
ENV GOOS linux
ENV GO111MODULE on
RUN go install -v
RUN go build -v -o app


FROM ubuntu:latest
COPY --from=builder app .
RUN apt update 
RUN apt install -y ca-certificates
CMD ["./app"]
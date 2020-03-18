FROM golang:1.13 as builder

WORKDIR /app

COPY src .
COPY go.mod .

RUN go mod download
ENV CGO_ENABLED 0
ENV GOOS linux
RUN  go build -mod=readonly -v -o app


FROM ubuntu:latest
COPY --from=builder app .
ARG _BASE_URL
ENV _BASE_URL ${_BASE_URL}
RUN apt update 
RUN apt install -y ca-certificates
CMD ["./app"]
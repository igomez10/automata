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


FROM alpine:latest
COPY --from=builder app .
RUN apk update 
RUN apk add ca-certificates
CMD ["./app"]
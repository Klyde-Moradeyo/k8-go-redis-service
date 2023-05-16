## Build
FROM golang:1.14-alpine as builder

WORKDIR /app

COPY go.mod go.sum *.go ./

RUN go mod download

# CGO disabled as it simplifies deployment and  makes image is smaller
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

## Deploy
FROM alpine:latest

ENV PORT=8080

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]

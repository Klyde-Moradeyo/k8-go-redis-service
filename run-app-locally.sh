#!/bin/bash

export PORT=8080
export REDIS_HOST=localhost
export REDIS_PORT=6379
# export REDIS_PASSWORD=your_redis_password
export REDIS_DB=0

go mod download
go run main.go
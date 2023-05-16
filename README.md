# k8-go-redis-service

## Overview

This repository contains a simple golang service which serves a single endpoint: `/:id`. For each call to this endpoint, the service increments a counter, and returns the number of times the endpoint has been called for the given ID. State for the application is stored in and retrieved from redis, where the data is stored simply with `id` as the key, and the count as the value.

I am going to deploy this application, and all its dependencies (in this case, redis) on kubernetes. It will be accessible from outside the cluster via HTTP, and should be deployed with high-availability in mind

The entire solution should be able to run on an fresh ubuntu VM.

## Requirements

- Simple to build and run
- Application is able to be deployed on kubernetes and can be accessed from outside the cluster
- Application must be able to survive the failure of one or more instances while staying highly-available
- Redis must be password protected


## Building the Docker image
Read this [doc](https://docs.docker.com/registry/deploying/) to push the image to your local docker registry


FROM qdrant/qdrant:latest

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

USER 1000

FROM eclipse-temurin:8-jdk-jammy

ARG PIG_VERSION=0.17.0
ARG DATAFU_VERSION=1.6.1

ENV DEBIAN_FRONTEND=noninteractive \
    PIG_HOME=/opt/pig \
    PATH=/opt/pig/bin:${PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-pip \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://downloads.apache.org/pig/pig-${PIG_VERSION}/pig-${PIG_VERSION}.tar.gz \
    && tar -xzf pig-${PIG_VERSION}.tar.gz -C /opt \
    && mv /opt/pig-${PIG_VERSION} /opt/pig \
    && rm pig-${PIG_VERSION}.tar.gz

WORKDIR /app

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/lib \
    && wget -q -O /app/lib/datafu-pig-${DATAFU_VERSION}.jar \
       https://repo.maven.apache.org/maven2/org/apache/datafu/datafu-pig/${DATAFU_VERSION}/datafu-pig-${DATAFU_VERSION}.jar


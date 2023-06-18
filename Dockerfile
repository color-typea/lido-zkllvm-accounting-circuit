<<<<<<< HEAD
# build to ghcr.io/nilfoundation/zkllvm-template:latest
FROM ghcr.io/nilfoundation/build-base:1.76.0

RUN DEBIAN_FRONTEND=noninteractive \
    echo 'deb [trusted=yes]  http://deb.nil.foundation/ubuntu/ all main' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y --no-install-recommends --no-install-suggests install \
      build-essential \
      cmake \
      git \
      zkllvm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/zkllvm-template
=======
# syntax=docker/dockerfile:1
ARG BOOST_VERSION=1.81.0
ARG BOOST_VERSION_UNDERSCORED=1_81_0
ARG BOOST_SETUP_DIR=/opt/boost_${BOOST_VERSION_UNDERSCORED}
ARG BOOST_BUILD_DIRECTORY=/tmp/boost_${BOOST_VERSION_UNDERSCORED}

FROM ubuntu:22.04 as boost_builder
RUN DEBIAN_FRONTEND=noninteractive \
    set -xe \
    && apt-get update \
    && apt-get -y --no-install-recommends --no-install-suggests install \
        autoconf \
        automake \
        build-essential \
        wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# using global args with their default versions
ARG BOOST_VERSION
ARG BOOST_VERSION_UNDERSCORED
ARG BOOST_SETUP_DIR
ARG BOOST_BUILD_DIRECTORY

WORKDIR /tmp
RUN set -xe \
    && wget -q --no-check-certificate \
      https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION}/source/boost_${BOOST_VERSION_UNDERSCORED}.tar.gz \
    && mkdir ${BOOST_BUILD_DIRECTORY} \
    && tar -xvf boost_${BOOST_VERSION_UNDERSCORED}.tar.gz \
    && rm boost_${BOOST_VERSION_UNDERSCORED}.tar.gz

WORKDIR ${BOOST_BUILD_DIRECTORY}
RUN set -xe \
    && sh ./bootstrap.sh --prefix=${BOOST_SETUP_DIR} \
    && ./b2 --prefix=${BOOST_SETUP_DIR} \
    && ./b2 install --prefix=${BOOST_SETUP_DIR}



FROM ubuntu:22.04
LABEL Name=zkllvm-dev Version=0.0.1
# using global args with their default versions
ARG BOOST_SETUP_DIR
ARG WORKDIR=/opt/workdir

RUN echo 'deb [trusted=yes]  http://deb.nil.foundation/ubuntu/ all main' >>/etc/apt/sources.list \
    && apt update \
    && apt install -y zkllvm cmake build-essential git \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=boost_builder ${BOOST_SETUP_DIR} ${BOOST_SETUP_DIR}
ENV BOOST_ROOT=${BOOST_SETUP_DIR}
>>>>>>> 93ed5a2 (Added dockerfile)

# build to ghcr.io/nilfoundation/zkllvm-template:latest
FROM ghcr.io/nilfoundation/proof-market-toolchain:0.0.31 as proof_market

FROM ghcr.io/nilfoundation/zkllvm-template:0.0.58

RUN DEBIAN_FRONTEND=noninteractive \
    echo 'deb [trusted=yes]  http://deb.nil.foundation/ubuntu/ all main' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y --no-install-recommends --no-install-suggests install \
      python3 \
      autoconf \
      automake \
      build-essential \
      clang-12 \
      cmake \
      git \
      gnutls-dev \
      libc-ares-dev \
      libfmt-dev \
      libhwloc-dev \
      liblz4-dev \
      libprotobuf-dev \
      libsctp-dev \
      libssl-dev \
      libyaml-cpp-dev \
      pkg-config \
      ragel \
      systemtap-sdt-dev \
      wget \
      xfslibs-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=proof_market /proof-market-toolchain /opt/proof-market-toolchain
RUN cd /opt/proof-market-toolchain && rm -rf build && ./build.sh


WORKDIR /opt/circuit

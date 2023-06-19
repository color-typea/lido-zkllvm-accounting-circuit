# build to ghcr.io/nilfoundation/zkllvm-template:latest
FROM ghcr.io/nilfoundation/proof-market-toolchain:0.0.31 as proof_market

FROM ghcr.io/nilfoundation/zkllvm-template:0.0.58

COPY --from=proof_market /proof-market-toolchain /proof-market-toolchain

ARG ZKLLVM_VERSION=0.0.86


RUN DEBIAN_FRONTEND=noninteractive \
    echo 'deb [trusted=yes]  http://deb.nil.foundation/ubuntu/ all main' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y --no-install-recommends --no-install-suggests install \
      build-essential \
      cmake \
      git \
      zkllvm=${ZKLLVM_VERSION} \
      python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/circuit

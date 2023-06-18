from ghcr.io/nilfoundation/proof-market-toolchain:latest as proof_market_toolchain

WORKDIR /proof-market-toolchain/
RUN ./build.sh
RUN mv ./build/bin/proof-generator/proof-generator ./proof-generator && rm -rf ./build

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
      python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=proof_market_toolchain /proof-market-toolchain /opt/proof-market-toolchain
RUN mv /opt/proof-market-toolchain/proof-generator /usr/bin/proof-generator

# TODO: build transpiler in a separate stage
COPY transpiler /usr/bin/transpiler

WORKDIR /opt/circuit
# build to ghcr.io/nilfoundation/zkllvm-template:latest
FROM ghcr.io/nilfoundation/proof-market-toolchain:0.0.31 as proof_market

FROM ghcr.io/nilfoundation/zkllvm-template:0.0.58

COPY --from=proof_market /proof-market-toolchain /proof-market-toolchain

RUN DEBIAN_FRONTEND=noninteractive \
    echo 'deb [trusted=yes]  http://deb.nil.foundation/ubuntu/ all main' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y --no-install-recommends --no-install-suggests install \
      python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/circuit

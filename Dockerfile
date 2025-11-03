
FROM ubuntu:jammy-20251001

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c", "-o", "pipefail"]

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    arj \
    binutils \
    brotli \
    build-essential \
    ca-certificates \
    clang \
    cpio \
    curl \
    file \
    git \
    gzip \
    lhasa \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    lrzip \
    lzip \
    make \
    p7zip-full \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    rpm2cpio \
    sudo \
    tk-dev \
    unrar \
    unzip \
    wget \
    xz-utils \
    zip \
    zlib1g-dev \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running tests
RUN groupadd --gid 1000 testuser && \
    useradd --uid 1000 --gid testuser --shell /bin/bash --create-home testuser && \
    echo 'testuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install uv, pinned version
ARG UV_VERSION=0.9.7
RUN curl --proto '=https' --tlsv1.2 -LsSf https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-installer.sh | sh
RUN cp $HOME/.local/bin/uv /usr/local/bin/uv && uv --version

# Switch to non-root user
USER testuser


FROM ubuntu:jammy-20220815

ARG DEBIAN_FRONTEND=noninteractive

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

# pyenv
RUN git clone --branch v2.3.4 https://github.com/pyenv/pyenv.git /pyenv
ENV PYENV_ROOT /pyenv
RUN /pyenv/bin/pyenv install 2.7.16
# openssl version on jammy (3) is too new for python 3.6, and breaks :/
# workaround is to use clang to build it
# https://github.com/pyenv/pyenv/issues/2239#issuecomment-1079275184
RUN CC=clang /pyenv/bin/pyenv install 3.6.15
RUN /pyenv/bin/pyenv install 3.7.13
RUN /pyenv/bin/pyenv install 3.8.13
RUN /pyenv/bin/pyenv install 3.9.12
RUN /pyenv/bin/pyenv install 3.10.4

ENV PATH=/pyenv/bin:${PATH}

# Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY entrypoint.sh /entrypoint.sh

ARG UID=1010
ARG USERNAME=builder
RUN echo "root:root" | chpasswd \
    && adduser --disabled-password --uid "${UID}" --gecos "" "${USERNAME}" \
    && echo "${USERNAME}:${USERNAME}" | chpasswd \
    && echo "%${USERNAME}    ALL=(ALL)   NOPASSWD:    ALL" >> /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && adduser ${USERNAME} sudo

# Ensure sudo group users are not
# asked for a password when using
# sudo command by ammending sudoers file
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> \
    /etc/sudoers

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Set non-interactive frontend to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Optional locale settings from the first Dockerfile (if desired)
ENV LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# Set a default number of threads for ITK-based tools
ENV ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4

# Install general dependencies and FSL dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    git \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    zlib1g-dev \
    locales \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG="en_US.UTF-8"

# --- BEGIN ANTs INSTALLATION ---

ENV ANTSPATH="/opt/ants-2.4.3/" \
    PATH="/opt/ants-2.4.3:$PATH"

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           ca-certificates \
           curl \
           unzip \
    && rm -rf /var/lib/apt/lists/* \
    && echo "Downloading ANTs ..." \
    && curl -fsSL -o ants.zip \
       https://github.com/ANTsX/ANTs/releases/download/v2.4.3/ants-2.4.3-centos7-X64-gcc.zip \
    && unzip ants.zip -d /opt \
    && mv /opt/ants-2.4.3/bin/* /opt/ants-2.4.3 \
    && rm ants.zip

# --- END ANTs INSTALLATION ---

# Neurodebian/FSL installation steps from the second Dockerfile
RUN wget -O- http://neuro.debian.net/lists/bionic.us-ca.full \
    | tee /etc/apt/sources.list.d/neurodebian.sources.list \
    && apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9 \
    && apt-get update \
    && apt-get install -y --no-install-recommends fsl-core \
    && rm -rf /var/lib/apt/lists/*

# Set FSL environment variables
ENV FSLDIR=/usr/share/fsl/6.0
ENV PATH=$FSLDIR/bin:$PATH
RUN echo ". $FSLDIR/etc/fslconf/fsl.sh" >> ~/.bashrc

# Copy your templates and scripts
COPY templates/ /opt/app/templates/
COPY script/ /opt/app/script/

# Make your primary script executable
RUN chmod +x /opt/app/script/automate_preprocessing.sh

# Set working directory
WORKDIR /data

# Final entrypoint for the Dockerfile
ENTRYPOINT ["/opt/app/script/automate_preprocessing.sh"]

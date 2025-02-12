# Start with Debian slim (you can switch to Ubuntu or other Linux distributions)
FROM debian:bullseye-slim

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" \
    ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4

# Install all dependencies in one shot, then clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    # General build & utility tools
    wget gnupg ca-certificates git build-essential bzip2 cmake \
    curl unzip bc dc file locales nano sudo \
    # Python
    python3 python3-pip \
    # Libraries needed for FSL/ANTs
    zlib1g-dev libfontconfig1 libfreetype6 libgl1-mesa-dev libgl1-mesa-dri \
    libglu1-mesa-dev libgomp1 libice6 libopenblas-base libxcursor1 \
    libxft2 libxinerama1 libxrandr2 libxrender1 libxt6 \
    && rm -rf /var/lib/apt/lists/* \
    # Configure locales
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG="en_US.UTF-8"

# --- ANTs INSTALLATION ---
ENV ANTSPATH="/opt/ants-2.4.3/"
ENV PATH="${ANTSPATH}:${PATH}"

RUN echo "Downloading ANTs ..." \
    && curl -fsSL -o ants.zip \
       https://github.com/ANTsX/ANTs/releases/download/v2.4.3/ants-2.4.3-centos7-X64-gcc.zip \
    && unzip ants.zip -d /opt \
    && mv /opt/ants-2.4.3/bin/* /opt/ants-2.4.3 \
    && rm ants.zip

# --- FSL INSTALLATION ---
ENV FSLDIR="/opt/fsl-6.0.7.1"
ENV PATH="${FSLDIR}/bin:${PATH}"
ENV FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="${FSLDIR}/bin/fsltclsh" \
    FSLWISH="${FSLDIR}/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLMACHINELIST="" \
    FSLREMOTECALL="" \
    FSLGECUDAQ="cuda.q"

RUN echo "Installing FSL ..." \
    && curl -fsSL https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py \
       | python3 - -d /opt/fsl-6.0.7.1 -V 6.0.7.1

# Copy in templates and scripts
COPY templates/ /opt/app/templates/
COPY script/ /opt/app/script/

# Make script executable
RUN chmod +x /opt/app/script/automate_preprocessing.sh

# Set working directory
WORKDIR /data

# Final entrypoint
ENTRYPOINT ["/opt/app/script/automate_preprocessing.sh"]

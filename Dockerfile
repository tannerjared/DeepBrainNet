# DeepBrainNet — Brain Age Prediction Container
#
# Build:
#   docker build -t deepbrainnet .
#
# Run (using local build):
#   docker run --rm \
#     -v ./DeepBrainNet_in/:/data \
#     -v ./DeepBrainNet_out/:/output \
#     deepbrainnet -d /data/ -o /output/ -m /app/Models/DBN_model.h5
#
# Run with GPU (requires nvidia-container-toolkit):
#   docker run --rm --gpus all \
#     -v ./DeepBrainNet_in/:/data \
#     -v ./DeepBrainNet_out/:/output \
#     deepbrainnet -d /data/ -o /output/ -m /app/Models/DBN_model.h5
#
# For CPU-only inference add: -g -1

# ── Stage 1: install Python dependencies ─────────────────────────────────────
FROM tensorflow/tensorflow:2.15.0 AS deps

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: final image ──────────────────────────────────────────────────────
FROM deps AS final

LABEL org.opencontainers.image.title="DeepBrainNet" \
      org.opencontainers.image.description="CNN brain age prediction from T1 MRI scans" \
      org.opencontainers.image.source="https://github.com/tannerjared/DeepBrainNet"

WORKDIR /app
COPY . .

# Default entrypoint delegates to test.sh so the container accepts the same
# flags as the shell-script workflow (-d, -o, -m, -g).
ENTRYPOINT ["bash", "Script/test.sh"]

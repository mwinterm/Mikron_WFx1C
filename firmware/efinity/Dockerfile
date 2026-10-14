# Efinix Efinity, headless, for build-7i92t.sh: Ubuntu 22.04 with the
# libraries Efinity's own Python and Qt load. Efinity itself is not in the
# image -- its licence asks for a download from Efinix's support center --
# and is mounted from wherever it was unpacked.
#
# libsqlite3-0 matters: without it the Interface Designer fails to import,
# efx_run skips that step with a warning in outflow/<project>.log, every
# stage still says PASS, and efx_pgm writes no bitstream.
FROM ubuntu:22.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      libglib2.0-0 libgl1 libegl1 libopengl0 libfontconfig1 libfreetype6 libdbus-1-3 \
      libxkbcommon0 libx11-6 libx11-xcb1 libxext6 libxrender1 libxcb1 \
      libsqlite3-0 unzip bzip2 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ENV QT_QPA_PLATFORM=offscreen

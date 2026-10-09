# OpenEB 3.1.2 build for the Prophesee EVK1 (Gen3.1, 640x480) camera.
# OpenEB 4.0+ dropped EVK1 support, so 3.1.2 is the last open-source release that works.
# NOTE: this Dockerfile has not been built from scratch by its author; it reproduces the
# manual steps that worked inside an ubuntu:20.04 container. Report issues if a package name fails.
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git cmake build-essential usbutils wget \
    libopencv-dev libboost-all-dev libusb-1.0-0-dev \
    libprotobuf-dev protobuf-compiler libhdf5-dev hdf5-tools \
    libglew-dev libglfw3-dev libcanberra-gtk-module ffmpeg python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/prophesee-ai/openeb.git /openeb \
    && cd /openeb && git checkout 3.1.2

RUN mkdir -p /openeb/build && cd /openeb/build \
    && cmake .. -DBUILD_TESTING=OFF -DCOMPILE_PYTHON3_BINDINGS=OFF \
    && cmake --build . --config Release -- -j"$(nproc)"

# make the camera plugins findable in every shell
RUN echo 'source /openeb/build/utils/scripts/setup_env.sh' >> /root/.bashrc

WORKDIR /openeb/build
CMD ["bash"]

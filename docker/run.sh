#!/usr/bin/env bash
# Start the EVK1 container with USB, a display, and a shared data folder.
set -e
DATA_DIR="${1:-$HOME/evk1_data}"
mkdir -p "$DATA_DIR"
xhost +local:docker >/dev/null
sudo docker run -it --rm --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  -v "$DATA_DIR":/data \
  -e DISPLAY="$DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix \
  evk1:3.1.2 bash

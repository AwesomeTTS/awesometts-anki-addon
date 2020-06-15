#!/usr/bin/env bash

# start x-server
start-stop-daemon --start --pidfile ~/xvfb.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset
export DISPLAY=:99

python -m pytest tests

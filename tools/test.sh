#!/usr/bin/env bash

sudo apt-get install mplayer lame

for required_program in 'git' 'mplayer' 'python3' 'lame' 'pip3'
do
  hash ${required_program} 2>/dev/null || {
    echo >&2 "$required_program is required but it is not installed. Please install $required_program first."
    exit 1
  }
done

bash anki_testing/install_anki.sh

python3 -m pytest tests

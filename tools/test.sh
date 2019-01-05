#!/usr/bin/env bash

for required_program in 'git' 'mplayer' 'python3.6' 'lame' 'pip'
do
  hash ${required_program} 2>/dev/null || {
    echo >&2 "$required_program is required but it is not installed. Please install $required_program first."
    exit 1
  }
done

bash anki_testing/install_anki.sh

python3.6 -m pytest tests

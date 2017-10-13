#!/usr/bin/env bash

for required_program in 'git' 'mplayer' 'python3.6' 'lame' 'pip'
do
  hash $required_program 2>/dev/null || {
    echo >&2 "$required_program is required but it is not installed. Please install $required_program first."
    exit 1
  }
done

anki_dir='anki_root'

if [ ! -e "$anki_dir" ]
then
    echo "$anki_dir not detected, cloning from master"
    git clone https://github.com/dae/anki anki_root
    cd anki_root
    pip install -r requirements.txt
    ./tools/build_ui.sh
    cd ..
fi
python3.6 -m pytest tests

#!/bin/sh

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

set -e

# run like this:
# tools/package.sh ~/awesometts-releases/AwesomeTTS-v1.14.0.ankiaddon

if [ -z "$1" ]
then
    echo 'Please specify where you want to save the package.' 1>&2
    echo 1>&2
    echo "    Usage: $0 <target>" 1>&2
    echo "     e.g.: $0 ~/AwesomeTTS.zip" 1>&2
    exit 1
fi

target=$1

case $target in
    *.ankiaddon)
        ;;

    *)
        echo 'Expected target path to end in a ".ankiaddon" extension.' 1>&2
        exit 1
esac

case $target in
    /*)
        ;;

    *)
        target=$PWD/$target
esac

if [ -e "$target" ]
then
    echo 'Removing old package...'
    rm -fv "$target"
fi

oldPwd=$PWD
cd "$(dirname "$0")/.." || exit 1

echo 'Packing zip file...'
zip -9 "$target" \
    awesometts/blank.mp3 \
    awesometts/LICENSE.txt \
    awesometts/*.py \
    awesometts/gui/*.py \
    awesometts/gui/icons/*.png \
    awesometts/service/*.py \
    awesometts/service/*.js \
    user_files/README.txt \
    __init__.py \
    manifest.json

cd "$oldPwd" || exit 1

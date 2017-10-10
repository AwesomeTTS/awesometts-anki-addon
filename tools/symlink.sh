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

addon_id="301952613"

set -e

if [ -z "$1" ]
then
    echo 'Please specify your Anki addons directory.' 1>&2
    echo 1>&2
    echo "    Usage: $0 <target>" 1>&2
    echo "     e.g.: $0 ~/.local/share/Anki2/addons21" 1>&2
    exit 1
fi

target=${1%/}

case $target in
    */addons21)
        ;;

    *)
        echo 'Expected target path to end in "/addons21".' 1>&2
        exit 1
esac

case $target in
    /*)
        ;;

    *)
        target=$PWD/$target
esac

if [ ! -d "$target" ]
then
    echo "$target is not a directory." 1>&2
    exit 1
fi

mkdir -p "$target/$addon_id"

if [ -f "$target/$addon_id/awesometts/config.db" ]
then
    echo 'Saving configuration...'
    saveConf=$(mktemp /tmp/config.XXXXXXXXXX.db)
    cp -v "$target/$addon_id/awesometts/config.db" "$saveConf"
fi

if [ -d "$target/$addon_id/awesometts/.cache" ]
then
    echo 'Saving cache...'
    saveCache=$(mktemp -d /tmp/anki_cacheXXXXXXXXXX)
    cp -rv "$target/$addon_id/awesometts/.cache/*" "$saveCache/"
fi

echo 'Cleaning up...'
rm -fv "$target/$addon_id/__init__.py"*
rm -rfv "$target/$addon_id/awesometts"

oldPwd=$PWD
cd "$(dirname "$0")/.." || exit 1

echo 'Linking...'
ln -sv "$PWD/$addon_id/__init__.py" "$target"
ln -sv "$PWD/$addon_id/awesometts" "$target"

cd "$oldPwd" || exit 1

if [ -n "$saveConf" ]
then
    echo 'Restoring configuration...'
    mv -v "$saveConf" "$target/$addon_id/awesometts/config.db"
fi

if [ -n "$saveCache" ]
then
    echo 'Restoring cache...'
    mv -rv "$saveConf/*" "$target/$addon_id/awesometts/.cache/"
fi

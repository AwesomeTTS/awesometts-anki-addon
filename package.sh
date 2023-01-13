#!/bin/sh

VERSION_NUMBER=$1 # for example 0.1
GIT_TAG=v${VERSION_NUMBER}

echo "AWESOMETTS_VERSION='${VERSION_NUMBER}'" > awesometts/version.py
git commit -a -m "upgraded version to ${VERSION_NUMBER}"
git push
git tag -a ${GIT_TAG} -m "version ${GIT_TAG}"
git push origin ${GIT_TAG}

# create .addon file
tools/package.sh ~/anki-addons-releases/AwesomeTTS-${GIT_TAG}.ankiaddon

# sync 
rclone sync ~/anki-addons-releases/ dropbox:Anki/anki-addons-releases/

# if you need to undo a release:
# git tag -d v0.2
# git push --delete origin v0.2
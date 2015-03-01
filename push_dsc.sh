#!/bin/bash

echo "======================"
echo "Modifying setup.py"
echo "======================"

VSTRING=$(git describe --tags --long | sed -e "s/v//")
echo "VSTRING: ${VSTRING}"
sed -r -e "s/( *)version =/\1version = \"${VSTRING}\",/" ./setup.py.in > setup.py

echo "======================"
echo "Modifying stdeb.cfg"
echo "======================"

cp ./stdeb.cfg ./stdeb.cfg.in
DEBBUILD=$(grep Debian-Version: ./stdeb.cfg | sed -e "s/Debian-Version: //")
DEBBUILD=$((${DEBBUILD} + 1))
echo "DEBBUILD: ${DEBBUILD}"
sed -e "s/Debian\-Version:.*/Debian\-Version: ${DEBBUILD}/" ./stdeb.cfg.in > stdeb.cfg

echo "======================"
echo "Building package"
echo "======================"

rm -rf deb_dist
python ./setup.py --command-packages=stdeb.command sdist_dsc --suite="utopic"
cd ./deb_dist/bcam-${VSTRING}
debuild -S
cd ../../
dput ppa:snegovick/bcam-preview ./deb_dist/bcam_${VSTRING}-${DEBBUILD}_source.changes

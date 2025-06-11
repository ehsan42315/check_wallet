#!/bin/bash
mkdir -p checkwallet-deb/DEBIAN
mkdir -p checkwallet-deb/usr/bin
cp checkwallet.py checkwallet-deb/usr/bin/checkwallet

cat <<EOF > checkwallet-deb/DEBIAN/control
Package: checkwallet
Version: 1.0
Section: base
Priority: optional
Architecture: all
Depends: python3
Maintainer: YourName
Description: Multi-chain wallet CLI tool
EOF

dpkg-deb --build checkwallet-deb

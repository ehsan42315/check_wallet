#!/bin/bash
echo "[*] Building AppImage..."

APP="checkwallet"
mkdir -p AppDir/usr/bin
cp checkwallet.py AppDir/usr/bin/$APP
echo -e '#!/bin/bash\npython3 /usr/bin/checkwallet "$@"' > AppDir/AppRun
chmod +x AppDir/AppRun

wget -O appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool
./appimagetool AppDir

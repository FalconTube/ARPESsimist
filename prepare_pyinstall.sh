rm -rf pyinst_dir
pip install --quiet -U PyInstaller
mkdir pyinst_dir
cp -r arpessimist/src/* pyinst_dir
cd pyinst_dir
sed -i 's/from \./from /' *.py
cp ../arpessimist/main_gui.py .
sed -i 's/from .src./from /' main_gui.py
sed -i "s/def run():/if __name__ == '__main__':/" main_gui.py
pyinstaller main_gui.py --onefile --hidden-import=pywt._extensions._cwt
cd dist
echo "ls of dist in pyinstall"
ls
mv main_gui* ../../dist/ARPESsimist.exe

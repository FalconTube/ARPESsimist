rm -rf pyinst_dir
pip install --quiet -U PyInstaller
pip install -U pypiwin32
mkdir pyinst_dir
cp -r arpessimist/src/* pyinst_dir
cd pyinst_dir
sed -i 's/from \./from /' *.py
cp ../arpessimist/main_gui.py .
sed -i 's/from .src./from /' main_gui.py
sed -i "s/def run():/if __name__ == '__main__':/" main_gui.py
pyinstaller main_gui.py --windowed --onefile --hidden-import=pywt._extensions._cwt
cd dist
echo "ls of dist in pyinstall"
ls
pyi-grab_version ARPESsimist.exe 
pyi-grab_version ARPESsimist.exe > arpessimst_version.txt
mv arpessimst_version.txt ..
cd ..
pyinstaller main_gui.py --windowed --onefile --version-file=arpessimst_version.txt --hidden-import=pywt._extensions._cwt
cd dist
mv main_gui* ../../dist/ARPESsimist.exe

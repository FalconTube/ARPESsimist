rm -rf pyinst_dir
pip install --quiet -U PyInstaller
pip install --quiet -U pypiwin32
mkdir pyinst_dir
cp -r arpessimist/src/* pyinst_dir
cd pyinst_dir
sed -i 's/from \./from /' *.py
cp ../arpessimist/main_gui.py .
sed -i 's/from .src./from /' main_gui.py
sed -i "s/def run():/if __name__ == '__main__':/" main_gui.py
#pyi-grab_version cmd.exe arpessimst_version.txt
#du -sh arpessimst_version.txt
#cp arpessimst_version.txt ../dist/
cp ../windows_version.txt .
pyinstaller main_gui.py --debug all --onedir --name=ARPESsimist --version-file=windows_version.txt --hidden-import=numpy.core --hidden-import=pywt._extensions._cwt
##pyinstaller main_gui.py --debug --onefile --name=ARPESsimist --version-file=arpessimst_version.txt --hidden-import=pywt._extensions._cwt
cd dist
echo "ls of dist in pyinstall"
ls
7z a dist 
mv dist.7z ../../dist/
#mv * ../../dist/

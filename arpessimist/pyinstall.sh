curr_dir="$(pwd)"
source="$curr_dir/src"
echo $source
pyinstaller --onefile --distpath pyinst -p $source main_gui.py

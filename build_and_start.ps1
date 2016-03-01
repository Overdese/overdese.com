python.exe ./poole.py -b --md-ext extra
Remove-Item -Recurse -Force ..\output\* -Exclude .git
Copy-Item .\output\* -Destination ..\output\ -Recurse -Force
python.exe ./poole.py -s


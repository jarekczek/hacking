@echo off

if x%1 == x goto usage
if %1 == 1 ( set par1=success& set par2=777& goto start )
if %1 == 2 ( set par1=failure& set par2=888& goto start )
goto usage

:usage

echo Usage: example_service ^<config_number^>
echo config_number: 1 or 2
goto kon

:start

if %par1% == success goto simulateSuccess
if %par1% == failure goto simulateFailure

goto real
goto simulateSuccess
goto simulateFailure

:simulateSuccess

echo starting %par1% %par2%
timeout /t 1
echo preparing
timeout /t 1
echo started successfully
goto loop

:simulateFailure

echo starting _%par1%_ _%par2%_
timeout /t 1
echo preparing
timeout /t 1
echo problem

goto kon


:loop
goto loop

:kon

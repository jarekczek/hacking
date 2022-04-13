@echo off

goto %1

:dump
curl localhost:7978/dump
goto kon

:add
echo haslo1 >%~dp0\input.txt
echo haslo2 >>%~dp0\input.txt
curl localhost:7978/add/test --data-binary "@%~dp0\input.txt"
goto kon

:mark
curl localhost:7978/markUsed/host2 -d "haslo2"
goto kon

:get
curl localhost:7978/getNotUsed/host
goto kon

:end
curl localhost:7978/shutdown
goto kon

:kon

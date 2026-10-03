@echo off
rem Console des checks de Pikmin 3 (beta) : affiche chaque check accompli pendant que tu joues.
chcp 65001 >nul
title Console des checks - Pikmin 3 (beta)
py -3.13 "%~dp0console_checks.py"
pause

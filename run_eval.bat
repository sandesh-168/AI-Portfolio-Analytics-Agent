@echo off
title AI Portfolio Agent Evaluator Benchmark
echo Running Ground Truth Benchmark Evaluation...
"%~dp0python_env\python.exe" "%~dp0agent_evaluator.py"
pause

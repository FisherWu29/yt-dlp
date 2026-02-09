#!/usr/bin/env bash
# exit on error
set -o errexit

# 只安装 Python 依赖
pip install --upgrade pip
pip install -r requirements.txt

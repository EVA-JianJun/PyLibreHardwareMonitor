# PyLibreHardwareMonitor
[![LibreHardwareMonitor](https://img.shields.io/badge/LibreHardwareMonitor-All%20Releases-3eb910)](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) [![Windows](https://img.shields.io/badge/Windows-10%20&%2011-blue)]() [![Python](https://img.shields.io/badge/Python-3.6+-e14d43)]()

[English](https://github.com/EVA-JianJun/PyLibreHardwareMonitor/blob/main/README.md) | 中文

[LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) 的 Python 封装, 快速调用 LibreHardwareMonitorLib 的原版功能.

## 它可以做什么?
您可以从下列设备读取信息:
- 主板
- Intel 和 AMD 处理器
- Intel 和 AMD 显卡
- 硬盘、固态硬盘和 NVMe 硬盘
- 网卡

## 安装
``` shell
pip install PyLibreHardwareMonitor
```

## 使用
``` Python
from PyLibreHardwareMonitor import Computer
computer = Computer()

# 获取系统信息, 每次调用自动刷新
computer.cpu
computer.gpu
computer.memory
computer.network
computer.storage
computer.motherboard
computer.controller
```

## 注意
仅支持 Windows, 由于是通过 .net 调用了 LibreHardwareMonitor, 所以运行效率不是太高. 相比 psutil 等库, 可以方便的获取 Intel 和 AMD 显卡信息.
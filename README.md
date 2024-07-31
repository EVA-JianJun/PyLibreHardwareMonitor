# PyLibreHardwareMonitor
[![LibreHardwareMonitor](https://img.shields.io/badge/LibreHardwareMonitor-All%20Releases-3eb910)](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) [![Windows](https://img.shields.io/badge/Windows-10%20&%2011-blue)]() [![Python](https://img.shields.io/badge/Python-3.6+-e14d43)]()

[简体中文 readme](https://github.com/EVA-JianJun/PyLibreHardwareMonitor/blob/main/README.cn.md)

Python wrapper for [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor), quick access to LibreHardwareMonitorLib's original functionality.

## What can it do?
You can read information from devices such as:
- Motherboards
- Intel and AMD processors
- NVIDIA and AMD graphics cards
- HDD, SSD and NVMe hard drives
- Network cards

## Installing
``` shell
pip install PyLibreHardwareMonitor
```

## Using
``` Python
from PyLibreHardwareMonitor import Computer
computer = Computer()

# Get system information, automatically refreshed with each call.
computer.cpu
computer.gpu
computer.memory
computer.network
computer.storage
computer.motherboard
computer.controller
```

## Note
Windows only, not very efficient since LibreHardwareMonitor is called from .net. Compared to libraries like psutil, it's easy to get Intel and AMD graphics card information.
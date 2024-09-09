import os
import atexit
import traceback

from PyLibreHardwareMonitorLib import dll
from rich.console import Console

class Computer:

    def __init__(self,
                 IsCpuEnabled: bool = False,
                 IsGpuEnabled: bool = False,
                 IsMemoryEnabled: bool = False,
                 IsMotherboardEnabled: bool = False,
                 IsControllerEnabled: bool = False,
                 IsNetworkEnabled: bool = False,
                 IsStorageEnabled: bool = False,
                 version: str = "latest") -> None:
        """
        init Computer instance.

        参数:
        IsCpuEnabled (bool): Enable CPU monitoring, default is False.
        IsGpuEnabled (bool): Enable Gpu monitoring, default is False.
        IsMemoryEnabled (bool): Enable Memory monitoring, default is False.
        IsMotherboardEnabled (bool): Enable Motherboard monitoring, default is False.
        IsControllerEnabled (bool): Enable Controller monitoring, default is False.
        IsNetworkEnabled (bool): Enable Network monitoring, default is False.
        IsStorageEnabled (bool): Enable Storage monitoring, default is False.

        ** If no parameters are passed, then all parameters are set to True. **

        version (str): Specify the version of LibreHardwareMonitorLib, the default is the latest version..
        """
        self.version = version

        if not any([IsCpuEnabled, IsGpuEnabled, IsMemoryEnabled, IsMotherboardEnabled, IsControllerEnabled, IsNetworkEnabled, IsStorageEnabled]):
            # all default False, set to True
            self._enable_cpu = True
            self._enable_gpu = True
            self._enable_memory = True
            self._enable_motherboard = True
            self._enable_controller = True
            self._enable_network = True
            self._enable_storage = True
        else:
            self._enable_cpu = IsCpuEnabled
            self._enable_gpu = IsGpuEnabled
            self._enable_memory = IsMemoryEnabled
            self._enable_motherboard = IsMotherboardEnabled
            self._enable_controller = IsControllerEnabled
            self._enable_network = IsNetworkEnabled
            self._enable_storage = IsStorageEnabled

        self._console = Console()
        if self._load_dll():
            self._init_monitor()

    def _load_dll(self) -> bool:
        """ Load  LibreHardwareMonitorLib """
        try:
            self.load_sucess = False
            import clr
            clr.AddReference(dll["HidSharp"].replace('.dll', ''))
            clr.AddReference(dll[self.version].replace('.dll', ''))
            self.version = dll['latest_version']
            from LibreHardwareMonitor.Hardware import Computer
            self._Computer = Computer
            self.load_sucess = True
        except Exception as err:
            self._console.print(f"[bold red blink]PyLibreHardwareMonitor: load dll err![/]")
            if os.name == 'nt':
                traceback.print_exc()
                print(err)
            return False
        else:
            return True

    def _init_monitor(self) -> None:
        """ Initialize the monitor and refresh the data """
        components = [
            ("cpu", self._enable_cpu),
            ("gpu", self._enable_gpu),
            ("memory", self._enable_memory),
            ("motherboard", self._enable_motherboard),
            ("controller", self._enable_controller),
            ("network", self._enable_network),
            ("storage", self._enable_storage)
        ]

        for component_name, is_enabled in components:
            if is_enabled:
                self._init_component_monitor(component_name)

    def _init_component_monitor(self, component_name: str) -> None:
        """ Initialize a specific component monitor """
        try:
            monitor = self._Computer()
            setattr(self, f"_{component_name}_monitor", monitor)
            setattr(monitor, f"Is{component_name.capitalize()}Enabled", True)
            monitor.Open()
            atexit.register(monitor.Close)
        except Exception as err:
            self._console.print(f"[bold red blink]{component_name.capitalize()} Error: {err}![/]")

    def _update_monitor(self, monitor) -> dict:
        """ Update monitor """
        monitor_info = {}
        try:
            same_name_hardware_dict = {}
            for hardware in monitor.Hardware:
                # get hardware_info
                hardware_info = {}
                hardware.Update()  # refresh update info
                for sensor in hardware.Sensors:
                    SensorType = sensor.SensorType.ToString()
                    hardware_info.setdefault(SensorType, {})[sensor.Name] = sensor.Value

                # save hardware_info
                if hardware.Name in same_name_hardware_dict:
                    same_name_hardware_dict[hardware.Name].append(hardware_info)  # save three+
                else:
                    if hardware.Name in monitor_info:  # hardware name is the same, eg: same type of hard disk
                        same_name_hardware_dict.setdefault(hardware.Name, []).append(monitor_info.pop(hardware.Name))
                        same_name_hardware_dict[hardware.Name].append(hardware_info)
                    else:
                        monitor_info[hardware.Name] = hardware_info

            # add same hardware info
            for hardware_name, hardware_info_list in same_name_hardware_dict.items():
                for index, hardware_info in enumerate(hardware_info_list, start=1):
                    monitor_info[f"{hardware_name}-{index}"] = hardware_info

        except Exception as err:
            self._console.print(f"[bold red blink]PyLibreHardwareMonitor: update monitor err![/]")
            traceback.print_exc()
            print(err)
        finally:
            return monitor_info

    @property
    def cpu(self) -> dict:
        try:
            return self._update_monitor(self._cpu_monitor)
        except AttributeError:
            return {}

    @property
    def gpu(self) -> dict:
        try:
            return self._update_monitor(self._gpu_monitor)
        except AttributeError:
            return {}

    @property
    def memory(self) -> dict:
        try:
            return self._update_monitor(self._memory_monitor)
        except AttributeError:
            return {}

    @property
    def motherboard(self) -> dict:
        try:
            return self._update_monitor(self._motherboard_monitor)
        except AttributeError:
            return {}

    @property
    def controller(self) -> dict:
        try:
            return self._update_monitor(self._controller_monitor)
        except AttributeError:
            return {}

    @property
    def network(self) -> dict:
        try:
            return self._update_monitor(self._network_monitor)
        except AttributeError:
            return {}

    @property
    def storage(self) -> dict:
        try:
            return self._update_monitor(self._storage_monitor)
        except AttributeError:
            return {}
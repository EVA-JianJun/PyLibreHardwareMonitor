"""
A simple toy.
"""
from PyLibreHardwareMonitor import Computer

import re
import time

from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from rich.columns import Columns
from rich.live import Live
from rich.measure import Measurement
from rich.style import Style

CPU_LOAD_SYMBOL = "■"
CPU_CORE_LOAD_SYMBOL = "▪"
TEMPERATURE_SYMBOL = "۰"
HISTOGRAM_SYMBOL_HIGHT = "█"
HISTOGRAM_UP_SYMBOL_LOW = "▄"
HISTOGRAM_DOWN_SYMBOL_LOW = "▀"
HISTOGRAM_VOID_SYMBOL = Text(" ", style=Style(color="color(255)"))

class Top():
    """ Windows Top """
    def __init__(self):
        """ init Top """

        self._computer = Computer() # computer monitor
        self._console = Console() # rich console

        # cpu
        self._cpu_load_pattern = re.compile(r'CPU Core #(\d+) Thread #(\d+)')
        self._cpu_temperature_pattern = re.compile(r'CPU Core #(\d+)$')
        self._cpu_clock_pattern = re.compile(r'CPU Core #(\d+)$')

        self._cpu_core_load_cache = {} # CPU 核心负载缓存信息
        self._cpu_temperature_cache = {} # CPU 核心温度缓存信息
        self._up_histogram_text_cache_list = [] # CPU 负载柱状图文本缓存

    def _parsing_cpu_info(self):
        cpu_info_dict = self._computer.cpu
        cpu_info_parsing = {}
        for cpu_name, cpu_info in cpu_info_dict.items():

            # 统计 CPU 各个核心所有线程负载信息
            cpu_core_load_values = {}
            for key, value in cpu_info['Load'].items():
                match = self._cpu_load_pattern.search(key)
                if match:
                    core_num = match.group(1) # 核心编号
                    if core_num not in cpu_core_load_values:
                        cpu_core_load_values[core_num] = []
                    cpu_core_load_values[core_num].append(value)

            cpu_core_load_dict = {core_num: sum(values) / len(values) for core_num, values in cpu_core_load_values.items()}

            # 统计 CPU 各个核心温度信息
            cpu_core_temperature_dict = {}
            for key, value in cpu_info['Temperature'].items():
                match = self._cpu_temperature_pattern.search(key)
                if match:
                    core_num = match.group(1) # 核心编号
                    cpu_core_temperature_dict[core_num] = value

            # 统计 CPU 核心频率
            cpu_core_clock_list = []
            for key, value in cpu_info['Clock'].items():
                match = self._cpu_clock_pattern.search(key)
                if match:
                    cpu_core_clock_list.append(value)
            tolal_clock = sum(cpu_core_clock_list) / len(cpu_core_clock_list) / 1000

            tolal_power = cpu_info['Power']['CPU Package'] # 总功耗
            tolal_voltage = cpu_info['Voltage']['CPU Core'] # 总电压
            total_load = cpu_info['Load']['CPU Total'] # 总负载
            total_temperature = cpu_info['Temperature']['CPU Package'] # 总温度


            cpu_info_parsing[cpu_name] = {
                "load" : cpu_core_load_dict,
                "temperature" : cpu_core_temperature_dict,
                "tolal_clock" : tolal_clock,
                "tolal_power" : tolal_power,
                "tolal_voltage" : tolal_voltage,
                "total_load" : total_load,
                "total_temperature" : total_temperature,
            }

        return cpu_info_parsing

    def _get_histogram_color(self, percentage):
        # 颜色从绿到红的渐变, 100 个档位
        colors = {
            0: "#00FF00",
            1: "#02FC00",
            2: "#05F900",
            3: "#07F700",
            4: "#0AF400",
            5: "#0CF200",
            6: "#0FEF00",
            7: "#12EC00",
            8: "#14EA00",
            9: "#17E700",
            10: "#19E500",
            11: "#1CE200",
            12: "#1EE000",
            13: "#21DD00",
            14: "#24DA00",
            15: "#26D800",
            16: "#29D500",
            17: "#2BD300",
            18: "#2ED000",
            19: "#30CE00",
            20: "#33CB00",
            21: "#36C800",
            22: "#38C600",
            23: "#3BC300",
            24: "#3DC100",
            25: "#40BE00",
            26: "#42BC00",
            27: "#45B900",
            28: "#48B600",
            29: "#4AB400",
            30: "#4DB100",
            31: "#4FAF00",
            32: "#52AC00",
            33: "#55AA00",
            34: "#57A700",
            35: "#5AA400",
            36: "#5CA200",
            37: "#5F9F00",
            38: "#619D00",
            39: "#649A00",
            40: "#679700",
            41: "#699500",
            42: "#6C9200",
            43: "#6E9000",
            44: "#718D00",
            45: "#738B00",
            46: "#768800",
            47: "#798500",
            48: "#7B8300",
            49: "#7E8000",
            50: "#807E00",
            51: "#837B00",
            52: "#857900",
            53: "#887600",
            54: "#8B7300",
            55: "#8D7100",
            56: "#906E00",
            57: "#926C00",
            58: "#956900",
            59: "#976700",
            60: "#9A6400",
            61: "#9D6100",
            62: "#9F5F00",
            63: "#A25C00",
            64: "#A45A00",
            65: "#A75700",
            66: "#AA5500",
            67: "#AC5200",
            68: "#AF4F00",
            69: "#B14D00",
            70: "#B44A00",
            71: "#B64800",
            72: "#B94500",
            73: "#BC4200",
            74: "#BE4000",
            75: "#C13D00",
            76: "#C33B00",
            77: "#C63800",
            78: "#C83600",
            79: "#CB3300",
            80: "#CE3000",
            81: "#D02E00",
            82: "#D32B00",
            83: "#D52900",
            84: "#D82600",
            85: "#DA2400",
            86: "#DD2100",
            87: "#E01E00",
            88: "#E21C00",
            89: "#E51900",
            90: "#E71700",
            91: "#EA1400",
            92: "#EC1200",
            93: "#EF0F00",
            94: "#F20C00",
            95: "#F40A00",
            96: "#F70700",
            97: "#F90500",
            98: "#FC0200",
            99: "#FF0000",
           100: "#FF0000",
        }
        return colors[int(percentage)]

    def _get_load_color(self, percentage):
        # 颜色从绿到红的渐变
        colors = [
            "#00FF00",  # 绿色
            "#33FF00",
            "#66FF00",
            "#99FF00",
            "#CCFF00",
            "#FFFF00",  # 黄色
            "#FFCC00",
            "#FF9900",
            "#FF6600",
            "#FF3300",
            "#FF0000"   # 红色
        ]
        index = int(percentage / 10)  # 将百分比转换为0-10的索引
        return colors[index]

    def fresh_core_text(self, name: str, core_load: float):
        style = self._get_load_color(core_load)
        try:
            self._cpu_core_load_cache[name]
        except KeyError:
            self._cpu_core_load_cache[name] = {}
            self._cpu_core_load_cache[name]['last'] = core_load
            self._cpu_core_load_cache[name]['text'] = Text(CPU_CORE_LOAD_SYMBOL, style=style) + Text(CPU_CORE_LOAD_SYMBOL * 9, style="color(8)")
        else:
            if core_load > self._cpu_core_load_cache[name]['last']:
                self._cpu_core_load_cache[name]['text'] = Text(CPU_CORE_LOAD_SYMBOL, style=style) + self._cpu_core_load_cache[name]['text'][:-1]
            else:
                self._cpu_core_load_cache[name]['text'] = Text(CPU_CORE_LOAD_SYMBOL, style="color(8)") + self._cpu_core_load_cache[name]['text'][:-1]
            self._cpu_core_load_cache[name]['last'] = core_load

    def fresh_temperature_text(self, name: str, temperature: float):
        try:
            self._cpu_temperature_cache[name]
        except KeyError:
            self._cpu_temperature_cache[name] = {}
            self._cpu_temperature_cache[name]['last'] = temperature
            self._cpu_temperature_cache[name]['text'] = Text(TEMPERATURE_SYMBOL, style="color(27)") + Text(TEMPERATURE_SYMBOL * 7, style="color(8)")
        else:
            if temperature > self._cpu_temperature_cache[name]['last']:
                self._cpu_temperature_cache[name]['text'] = Text(TEMPERATURE_SYMBOL, style="color(27)") + self._cpu_temperature_cache[name]['text'][:-1]
            else:
                self._cpu_temperature_cache[name]['text'] = Text(TEMPERATURE_SYMBOL, style="color(8)") + self._cpu_temperature_cache[name]['text'][:-1]
            self._cpu_temperature_cache[name]['last'] = temperature

    def fresh_histogram_text(self, total_load: float, height: int, width: int):
        fix_height = int(height)
        min_part = 1 / height # 最小分割步长, 用来比较输出符号
        for row in range(fix_height):
            div = total_load / 100 - row / fix_height
            if div > 0: # show symbol
                if div > min_part:
                    try:
                        self._up_histogram_text_cache_list[row] = Text(HISTOGRAM_SYMBOL_HIGHT, style=self._get_histogram_color(total_load)) + self._up_histogram_text_cache_list[row]
                        # self._down_histogram_text_cache_list[row] = Text(HISTOGRAM_SYMBOL_HIGHT, style=self._get_histogram_color(total_load)) + self._down_histogram_text_cache_list[row]
                    except IndexError:
                        self._up_histogram_text_cache_list.append(Text(HISTOGRAM_SYMBOL_HIGHT, style=self._get_histogram_color(total_load)))
                        # self._down_histogram_text_cache_list.append(Text(HISTOGRAM_SYMBOL_HIGHT, style=self._get_histogram_color(total_load)))
                else:
                    try:
                        self._up_histogram_text_cache_list[row] = Text(HISTOGRAM_UP_SYMBOL_LOW, style=self._get_histogram_color(total_load)) + self._up_histogram_text_cache_list[row]
                        # self._down_histogram_text_cache_list[row] = Text(HISTOGRAM_DOWN_SYMBOL_LOW, style=self._get_histogram_color(total_load)) + self._down_histogram_text_cache_list[row]
                    except IndexError:
                        self._up_histogram_text_cache_list.append(Text(HISTOGRAM_UP_SYMBOL_LOW, style=self._get_histogram_color(total_load)))
                        # self._down_histogram_text_cache_list.append(Text(HISTOGRAM_DOWN_SYMBOL_LOW, style=self._get_histogram_color(total_load)))
            else: # not show
                try:
                    self._up_histogram_text_cache_list[row] = HISTOGRAM_VOID_SYMBOL + self._up_histogram_text_cache_list[row]
                    # self._down_histogram_text_cache_list[row] = HISTOGRAM_VOID_SYMBOL + self._down_histogram_text_cache_list[row]
                except IndexError:
                    self._up_histogram_text_cache_list.append(HISTOGRAM_VOID_SYMBOL)
                    # self._down_histogram_text_cache_list.append(HISTOGRAM_VOID_SYMBOL)

        # fix to width
        for index, text in enumerate(self._up_histogram_text_cache_list):
            self._up_histogram_text_cache_list[index] = text[:width]
        # for index, text in enumerate(self._down_histogram_text_cache_list):
            # self._down_histogram_text_cache_list[index] = text[:width]

    def get_panel_content(self):
        cpu_info_parsing = self._parsing_cpu_info() # 获取 CPU 状态
        # cpu_info_parsing['Intel Core i7-10700 - 2'] = cpu_info_parsing['Intel Core i7-10700'] # DEBUG

        cpu_core_panel_list = []
        cpu_core_panel_width = 0
        max_cpu_core_num = 0
        for cpu_name, cpu_info in cpu_info_parsing.items():
            title = Text("{0} - ".format(cpu_name)) + Text("{0:.1f}".format(cpu_info['tolal_clock']), style="color(9)") + Text(" GHz")

            # 构造 CPU 占用率字符
            total_load = cpu_info['total_load']
            load_style = self._get_load_color(total_load)
            load_symbol_num = int(total_load // 10)
            not_load_symbol_num = 10 - load_symbol_num

            cpu_text = Text()

            total_cpu_text = Text()
            total_cpu_text.append("CPU ", style="color(10)")
            total_cpu_text.append(CPU_LOAD_SYMBOL * load_symbol_num, style=load_style)
            total_cpu_text.append(CPU_LOAD_SYMBOL * not_load_symbol_num, style="color(8)")
            total_cpu_text.append("{0:3.0f}".format(total_load), style=load_style)
            total_cpu_text.append("% ", style="color(15)")
            self.fresh_temperature_text('total_temperature', cpu_info['total_temperature'])
            total_cpu_text.append(self._cpu_temperature_cache['total_temperature']['text'])
            total_cpu_text.append(" {0}".format(int(cpu_info['total_temperature'])), style="color(13)")
            total_cpu_text.append("°C\n", style="color(15)")

            cpu_text.append(total_cpu_text)

            if len(cpu_info['load']) > max_cpu_core_num:
                max_cpu_core_num = len(cpu_info['load'])

            for core_num, core_load in cpu_info['load'].items():
                load_style = self._get_load_color(core_load)
                load_symbol_num = int(core_load // 10 + 1)
                not_load_symbol_num = 10 - load_symbol_num

                cpu_core_text = Text()
                cpu_core_text.append("C{0}  ".format(core_num), style="color(15)")

                # 1.starus
                # self.fresh_core_text(core_num, core_load)
                # cpu_core_text.append(self._cpu_core_load_cache[core_num]["text"])

                # 2.load
                cpu_core_text.append(CPU_CORE_LOAD_SYMBOL * load_symbol_num, style=load_style)
                cpu_core_text.append(CPU_CORE_LOAD_SYMBOL * not_load_symbol_num, style="color(8)")

                cpu_core_text.append("{0:3.0f}".format(core_load), style=load_style)
                cpu_core_text.append("% ", style="color(15)")
                self.fresh_temperature_text(core_num, cpu_info['temperature'][core_num])
                cpu_core_text.append(self._cpu_temperature_cache[core_num]['text'])
                cpu_core_text.append(" {0}".format(int(cpu_info['temperature'][core_num])), style="color(13)")
                cpu_core_text.append("°C\n", style="color(15)")

                cpu_text.append(cpu_core_text)

            cpu_text.append(Text("Power: {0:.1f}W     Voltage: {1:.3f}V".format(cpu_info['tolal_power'], cpu_info['tolal_voltage'])))

            cpu_core_panel = Panel(
                renderable=cpu_text,
                title=title,
                title_align="left",
            )

            # 使用 Console 的 measure 方法来测量 Panel 的宽度
            measurement = Measurement.get(self._console, self._console.options, cpu_core_panel)
            cpu_core_panel_width += measurement.minimum # 取最小宽度

            cpu_core_panel_list.append(cpu_core_panel)

        histogram_width = self._console.width - cpu_core_panel_width - 8 - len(cpu_core_panel_list) # fix width
        histogram_height = max_cpu_core_num + 4

        self.fresh_histogram_text(total_load, histogram_height, histogram_width)

        histogram = Text()
        for text in reversed(self._up_histogram_text_cache_list):
            histogram += text + "\n"
        # for text in self._down_histogram_text_cache_list:
        #     histogram += text + "\n"
        histogram = histogram[:-1] # del "\n"

        # 创建包含 p_son 和 text 的 Columns
        columns = Columns(cpu_core_panel_list + [histogram])

        # 创建 p_parent Panel 包含 columns
        cpu_monitor_parent = Panel(columns, title="CPU", title_align="left", border_style="bold green")

        return cpu_monitor_parent

    def top(self):
        with Live(self.get_panel_content(), refresh_per_second=1, console=self._console) as live:
            while True:
                time.sleep(1)
                live.update(self.get_panel_content())

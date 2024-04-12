# -*- coding: utf-8 -*-

"""

"""


def progress_line(progress, start, end, cols) -> str:
    pb_width = cols - (len(start) + len(end) + 2)
    progress_bar = f'[{"#" * int(pb_width * progress):<{pb_width}}]'
    return f'{start}{progress_bar}{end}'

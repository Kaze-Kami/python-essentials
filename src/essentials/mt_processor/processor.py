# -*- coding: utf-8 -*-

"""

"""

import curses
import curses.ascii as keys
import os
import time

from concurrent.futures import ThreadPoolExecutor

from .task import Task, TaskStatus
from ..itertools.sorting import SortBy
from ..tui import ScrollableList
from ..tui.formatter import Formatter
from ..tui.utilities import progress_line
from ..io.format import duration


class _TaskFormatter(Formatter[Task]):
    def format(self, task: Task, max_chars: int) -> list[str]:
        base_message = f'[{task.name}] {task.status.name:<11} | {task.message}'
        if task.status == TaskStatus.IN_PROGRESS:
            eta_line = f' | ETA: {duration(task.eta)}'
            base_message = f'{base_message}{eta_line:>{max_chars - (len(base_message))}}'
            return [
                base_message,
                progress_line(task.progress, f'{task.progress:05.2%} in {duration(time.perf_counter() - task.start)} | ', '', max_chars),
            ]
        elif task.status == TaskStatus.COMPLETED:
            return [
                base_message,
                f'after {duration(task.end - task.start)}',
            ]
        elif task.status == TaskStatus.FAILED:
            return [
                base_message,
                f'after {duration(task.end - task.start)}: {task.error}',
            ]
        return [base_message]


class MTProcessor:
    def __init__(
            self,
            tasks: list[Task],
            num_workers: int = 5,
            shows_stats: bool = True,
            info_text: str = '',
            show_finished: bool = True,
            show_not_started: bool = True,
    ):
        self._tasks = tasks
        self._num_workers = num_workers
        self._show_stats = shows_stats
        self._info_text = info_text
        self._show_finished = show_finished
        self._show_not_started = show_not_started

    def run(self):
        curses.wrapper(self._main)

    def _main(self, screen):
        curses.curs_set(False)
        screen.nodelay(True)

        tasks = self._tasks
        completed = []
        failed = []

        t0 = time.perf_counter()

        def list_filter(task: Task) -> bool:
            if task.status == TaskStatus.NOT_STARTED:
                return self._show_not_started
            elif task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                return self._show_finished
            return True

        task_list = ScrollableList(tasks,
                                   formatter=_TaskFormatter(),
                                   filter=list_filter,
                                   sort=SortBy(
                                           lambda t: t.status,
                                           [TaskStatus.PREPARING, TaskStatus.IN_PROGRESS, TaskStatus.FAILED, TaskStatus.COMPLETED]
                                   ))

        with ThreadPoolExecutor(max_workers=self._num_workers) as pool:
            # queue tasks
            for task in tasks:
                pool.submit(task.execute)

            while len(completed) + len(failed) < len(tasks):
                completed = list(filter(lambda t: t.status == TaskStatus.COMPLETED, tasks))
                failed = list(filter(lambda t: t.status == TaskStatus.FAILED, tasks))
                in_progress = list(filter(lambda t: t.status == TaskStatus.IN_PROGRESS, tasks))
                finished = len(completed) + len(failed)

                total_progress = (finished + sum(t.progress for t in in_progress)) / len(tasks)

                screen.clear()
                rows, cols = screen.getmaxyx()

                screen.addstr(0, 0, f'Processing {len(tasks)} tasks: {total_progress:05.2%} ({len(tasks) - finished} remaining, {len(failed)} failed)')
                if total_progress == 0 or total_progress == 1 or len(in_progress) == 0:
                    eta = 0
                elif len(in_progress) < self._num_workers:
                    eta = max(t.eta for t in in_progress)
                else:
                    eta = (time.perf_counter() - t0) * (1.0 / total_progress - 1.0)
                eta_line = f'eta={duration(eta)}'
                screen.addstr(0, cols - len(eta_line), eta_line)
                screen.addstr(1, 0, progress_line(total_progress, f'{finished} / {len(tasks)} | ', '', cols))
                screen.hline(2, 0, '-', cols)

                line = self._write_info_text(3, screen)
                task_list.draw(line, 0, rows - line, screen)
                # task_list.draw(3, 0, 5, screen)

                screen.refresh()

                # check for ctrl-c
                ch = screen.getch()
                if keys.isctrl(ch) and keys.ctrl(ch) == keys.ETX:
                    # that's rather rude, but it works...
                    os.kill(os.getpid(), -1)
                elif ch == curses.KEY_UP:
                    task_list.scroll(-1)
                elif ch == curses.KEY_DOWN:
                    task_list.scroll(1)
                elif ch == curses.KEY_PPAGE:
                    task_list.scroll_page(-1)
                elif ch == curses.KEY_NPAGE:
                    task_list.scroll_page(1)

        t1 = time.perf_counter()
        dt = t1 - t0

        screen.nodelay(False)
        do_quit = not self._show_stats

        while not do_quit:
            screen.clear()
            rows, cols = screen.getmaxyx()

            screen.addstr(0, 0, 'Stats:')
            screen.addstr(1, 0, f'Completed {len(tasks)} tasks in {duration(dt)} (~{duration(dt / len(tasks))} / task)')
            screen.hline(2, 0, '-', cols)

            line = self._write_info_text(3, screen)
            line = task_list.draw(line, 0, cols - line, screen)
            # line = task_list.draw(3, 0, 5, screen)
            screen.hline(line, 0, '-', cols)
            screen.addstr(line + 1, 0, 'Press enter to continue...')

            screen.refresh()
            ch = screen.getch()

            if keys.ctrl(ch) == keys.LF:
                do_quit = True
            elif ch == curses.KEY_UP:
                task_list.scroll(-1)
            elif ch == curses.KEY_DOWN:
                task_list.scroll(1)
            elif ch == curses.KEY_PPAGE:
                task_list.scroll_page(-1)
            elif ch == curses.KEY_NPAGE:
                task_list.scroll_page(1)

    def _write_info_text(self, line, screen):
        if not self._info_text:
            return line

        rows, cols = screen.getmaxyx()
        if self._info_text:
            for l in self._info_text.split('\n'):
                screen.addstr(line, 0, l)
                line += 1
            screen.hline(line, 0, '-', cols)
            line += 1
        return line

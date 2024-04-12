# -*- coding: utf-8 -*-

"""

"""

from typing import TypeVar, Generic, Callable, Iterable

from .formatter import Formatter

_T = TypeVar('_T')


class ScrollableList(Generic[_T]):
    def __init__(self,
                 items: Iterable[_T],
                 formatter: Formatter[_T] or None = None,
                 filter: Callable[[_T], bool] or None = None,
                 sort: Callable[[_T], int] or None = None):
        self._items = items
        self._formatter = formatter
        self._filter = filter
        self._sort = sort
        self._max_lines = 0
        self._max_scroll = 0
        self._scroll_offset = 0
        self._scroll_buffer = 0
        self._page_scroll_buffer = 0

    def scroll(self, amount: int):
        self._scroll_buffer += amount

    def scroll_page(self, amount: int):
        self._page_scroll_buffer += amount

    def set_formatter(self, formatter: Formatter[_T] or None):
        self._formatter = formatter

    def set_filter(self, filter: Callable[[_T], bool] or None):
        self._filter = filter

    def set_sort(self, sort: Callable[[_T], int] or None):
        self._sort = sort

    def draw(self, x, y, max_lines, screen) -> int:
        rows, cols = screen.getmaxyx()
        # update scroll offset
        self._scroll_offset += self._scroll_buffer + self._page_scroll_buffer * max_lines
        self._scroll_buffer = 0
        self._page_scroll_buffer = 0

        # sort and filter items
        items = self._items
        if self._filter is not None:
            items = filter(self._filter, items)
        if self._sort is not None:
            items = sorted(items, key=self._sort)

        lines = []
        for item in items:
            if self._formatter is not None:
                lines.extend(self._formatter(item, cols - y))
            else:
                lines.append(item)
        count = len(lines)

        # calculate actual offset
        if self._scroll_offset < 0:
            self._scroll_offset = 0
        elif count <= self._scroll_offset:
            self._scroll_offset = 0

        if count < max_lines:
            self._scroll_offset = 0
        else:
            self._scroll_offset = min(self._scroll_offset, count - max_lines)

        offset = self._scroll_offset

        # todo: indicate more before and after
        # start = 0 if self._scroll_offset == 0 else 1
        # end = 1 if self._scroll_offset + max_lines < count else 0
        # count = max_lines - (start + end)
        #
        # for i, line in enumerate(lines[offset:offset + count]):
        #     screen.addstr(start + x + i, y, line)
        #
        # if start:
        #     screen.addstr(x, y, '[...]')
        # if end:
        #     screen.addstr(start + x + count, y, '[...]')

        # todo: for now: no indicator
        for i, line in enumerate(lines[offset:offset + max_lines]):
            screen.addstr(x + i, y, line)

        return x + min(count, max_lines)

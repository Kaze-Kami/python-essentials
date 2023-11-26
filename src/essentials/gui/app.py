# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

import ctypes
from dataclasses import dataclass

import OpenGL.GL as gl
import glfw
import imgui
import pystray
from PIL import Image
from imgui.integrations.glfw import GlfwRenderer

from essentials.gui.core import _CORE_LOGGER
from essentials.io.logging import log_call

_DWM = ctypes.windll.dwmapi


def GLFW_BOOL(value: bool):
    return glfw.TRUE if value else glfw.FALSE


@dataclass
class AppConfig:
    """
    Basic application configuration

    @note icon_path: must be an .ico file
    @note background_color: rgb values range from 0 to 1
    """
    width: int
    height: int
    title: str
    icon_path: str = None
    start_minimized: bool = False


class Window:
    def __init__(self, ptr):
        self._ptr = ptr
        self._background_color = (.1, .1, .1, 1.)

    @property
    def floating(self) -> bool:
        return bool(glfw.get_window_attrib(self._ptr, glfw.FLOATING))

    @floating.setter
    def floating(self, value: bool):
        glfw.set_window_attrib(self._ptr, glfw.FLOATING, GLFW_BOOL(value))

    @property
    def resizable(self) -> bool:
        return bool(glfw.get_window_attrib(self._ptr, glfw.RESIZABLE))

    @resizable.setter
    def resizable(self, value: bool):
        glfw.set_window_attrib(self._ptr, glfw.FLOATING, GLFW_BOOL(value))

    @property
    def background_color(self) -> (float, float, float, float):
        return self._background_color

    @background_color.setter
    def background_color(self, rgba: (float, float, float, float)):
        self._background_color = rgba

    @property
    def position(self) -> (int, int):
        return glfw.get_window_pos(self._ptr)

    @position.setter
    def position(self, pos: (int, int)):
        glfw.set_window_pos(self._ptr, *pos)


class App:
    def __init__(self, config: AppConfig):
        self._config = config
        self._logger = _CORE_LOGGER

        self._icon_image = None
        if config.icon_path is not None:
            self._icon_image = Image.open(config.icon_path)
        self._raw_window = self._init_glfw()
        self._imgui_impl = self._init_imgui()

        self._tray_icon = None
        if self._icon_image is not None:
            self._tray_icon = self._init_tray()

        self._should_exit = False
        self._logger.info('Initialization complete')

        # proxy for client side glfw functions
        self.window = Window(self._raw_window)

    def update(self):
        """
        Update method to be overwritten by client
        :return:
        """
        pass

    def render(self):
        """
        (ImGui) Render method to be overwritten by client
        :return:
        """
        pass

    def on_hide(self):
        """
        Callback to be overwritten by client
        :return:
        """
        pass

    def on_show(self):
        """
        Callback to be overwritten by client
        :return:
        """
        pass

    def on_move(self, pos: (int, int)):
        """
        Callback to be overwritten by client
        :param pos: new (x, y) position of window
        :return:
        """
        pass

    def on_start(self):
        """
        Callback to be overwritten by client
        :return:
        """
        pass

    def on_stop(self):
        """
        Callback to be overwritten by client
        :return:
        """
        pass

    def exit(self):
        """
        Close the application
        :return:
        """
        self._should_exit = True

    def run(self):
        """
        Main entry point for application
        :return:
        """
        try:
            # TODO: Maybe initialize application here, instead of in __init__
            if not self._config.start_minimized:
                self._show_window()

            self._should_exit = False
            if self._tray_icon is not None:
                self._tray_icon.run_detached()
            self.on_start()

            while not self._should_exit:
                glfw.poll_events()
                self._imgui_impl.process_inputs()

                if glfw.window_should_close(self._raw_window):
                    self._should_exit = True

                self.update()
                self._imgui_frame()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._logger.error(f'Exception while running: {e}')
            raise e
        finally:
            self._shutdown()

    # noinspection PyMethodMayBeStatic
    def get_additional_tray_actions(self) -> list[pystray.MenuItem]:
        """
        To be overwritten by client to provide additional tray icon actions
        :return: list of additional tray icon actions
        """
        return []

    # noinspection PyMethodMayBeStatic
    def get_additional_imgui_flags(self) -> int:
        """
        To be overwritten by client to provide additional imGui window flags
        to the 'main' window.
        For example: WINDOW_NO_TITLE_BAR to remove the title bar
        :return:
        """
        return 0

    @log_call(_CORE_LOGGER, name='Initialize GLFW')
    def _init_glfw(self):
        if not glfw.init():
            raise Exception("Could not initialize OpenGL context")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.FOCUSED, glfw.TRUE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.TRUE)

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(
                int(self._config.width), int(self._config.height), self._config.title, None, None
        )
        if not window:
            glfw.terminate()
            raise Exception("Could not initialize Window")

        # register callbacks
        glfw.set_window_iconify_callback(window, self._on_minimize)
        glfw.set_window_pos_callback(window, self._on_move)

        # window icon
        if self._icon_image is not None:
            glfw.set_window_icon(window, 1, [self._icon_image])

        # init opengl
        glfw.make_context_current(window)

        hndl = glfw.get_win32_window(window)

        # enable dark mode (see https://github.com/fyne-io/fyne/pull/2216/files)
        # check comp (aero) is  enabled (see https://stackoverflow.com/a/48207410/10330869)
        is_comp_enabled = ctypes.c_bool()
        err = _DWM.DwmIsCompositionEnabled(ctypes.byref(is_comp_enabled))
        if not err and is_comp_enabled:
            attr = 20  # DWMWA_USE_IMMERSIVE_DARK_MODE (see https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute)
            # see https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
            enabled = ctypes.c_int(1)
            err = _DWM.DwmSetWindowAttribute(hndl, attr, ctypes.byref(enabled), ctypes.sizeof(enabled))
            if err:
                _CORE_LOGGER.error(f'Unable to enable dark mode ({err=}')

        return window

    @log_call(_CORE_LOGGER, name='Initialize ImGui')
    def _init_imgui(self):
        imgui.create_context()
        imgui_impl = GlfwRenderer(self._raw_window)
        gl.glClearColor(0, 0, 0, 1.)
        return imgui_impl

    @log_call(_CORE_LOGGER, name='Initialize tray')
    def _init_tray(self):
        tray_icon = pystray.Icon(self._config.title, self._icon_image, self._config.title, menu=[
            pystray.MenuItem('', self._show_window, default=True, visible=False),
            *self.get_additional_tray_actions(),
            pystray.MenuItem('Exit', self._stop)
        ])
        return tray_icon

    def _imgui_frame(self):
        if not glfw.get_window_attrib(self._raw_window, glfw.VISIBLE):
            return

        io = self._imgui_impl.io

        imgui.new_frame()
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(*io.display_size)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.)
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.)
        imgui.push_style_color(imgui.COLOR_WINDOW_BACKGROUND, *self.window.background_color)
        imgui.begin('main', False,
                    imgui.WINDOW_NO_NAV |
                    imgui.WINDOW_NO_NAV_INPUTS |
                    imgui.WINDOW_NO_MOVE |
                    imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                    imgui.WINDOW_NO_COLLAPSE |
                    imgui.WINDOW_NO_TITLE_BAR |
                    imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS |
                    self.get_additional_imgui_flags())

        self.render()

        imgui.pop_style_color()
        imgui.pop_style_var(2)
        imgui.end()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        self._imgui_impl.render(imgui.get_draw_data())
        glfw.swap_buffers(self._raw_window)

    def _on_minimize(self, _, minimized):
        """
        glfw minify callback
        :return:
        """
        if minimized and self._tray_icon is not None:
            self.on_hide()
            glfw.hide_window(self._raw_window)

    def _on_move(self, _, x, y):
        """
        glfw window move callback
        :return:
        """
        self.on_move((x, y))

    def _show_window(self, *_):
        glfw.show_window(self._raw_window)
        glfw.restore_window(self._raw_window)
        glfw.focus_window(self._raw_window)
        self.on_show()

    def _stop(self, *_):
        self._should_exit = True

    @log_call(_CORE_LOGGER, name='Shutdown')
    def _shutdown(self):
        try:
            self.on_stop()
        except Exception as e:
            self._logger.error(f'Exception while running on_stop: {e}')
            raise e
        finally:
            self._imgui_impl.shutdown()
            glfw.terminate()
            if self._tray_icon is not None:
                self._tray_icon.stop()
            self._logger.info('Shutdown complete')

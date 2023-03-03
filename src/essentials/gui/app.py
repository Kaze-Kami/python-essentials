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


@dataclass
class AppConfig:
    width: int
    height: int
    title: str
    icon_path: str = None
    resizable: bool = False
    start_minimized: bool = False
    background_color: tuple[float, float, float] = (.1, .1, .1)


class App:
    def __init__(self, config: AppConfig):
        self._config = config
        self._logger = _CORE_LOGGER

        self._icon_image = None
        if config.icon_path is not None:
            self._icon_image = Image.open(config.icon_path)
        self._window = self._init_glfw()
        self._imgui_impl = self._init_imgui()

        self._tray_icon = None
        if self._icon_image is not None:
            self._tray_icon = self._init_tray()

        self._should_exit = False
        self._logger.info('Initialization complete')

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

                if glfw.window_should_close(self._window):
                    glfw.set_window_should_close(self._window, glfw.FALSE)
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

        if not self._config.resizable:
            glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(
                int(self._config.width), int(self._config.height), self._config.title, None, None
        )
        if not window:
            glfw.terminate()
            raise Exception("Could not initialize Window")

        glfw.set_window_iconify_callback(window, self._on_minimize)
        # window icon
        if self._icon_image is not None:
            glfw.set_window_icon(window, 1, [self._icon_image])

        # init opengl
        glfw.make_context_current(window)

        # enable dark mode (see https://github.com/fyne-io/fyne/pull/2216/files)
        hndl = glfw.get_win32_window(window)

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
        imgui_impl = GlfwRenderer(self._window)
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
        if not glfw.get_window_attrib(self._window, glfw.VISIBLE):
            return

        io = self._imgui_impl.io

        imgui.new_frame()
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(*io.display_size)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.)
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.)
        imgui.push_style_color(imgui.COLOR_WINDOW_BACKGROUND, *self._config.background_color, 1.0)
        imgui.begin('', False,
                    imgui.WINDOW_NO_NAV |
                    imgui.WINDOW_NO_NAV_INPUTS |
                    imgui.WINDOW_NO_MOVE |
                    imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                    imgui.WINDOW_NO_COLLAPSE |
                    imgui.WINDOW_NO_TITLE_BAR)

        self.render()


        imgui.pop_style_color()
        imgui.pop_style_var(2)
        imgui.end()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        self._imgui_impl.render(imgui.get_draw_data())
        glfw.swap_buffers(self._window)

    def _on_minimize(self, _, minimized):
        if minimized and self._tray_icon is not None:
            self.on_hide()
            glfw.hide_window(self._window)

    def _show_window(self, *_):
        glfw.show_window(self._window)
        glfw.restore_window(self._window)
        glfw.focus_window(self._window)
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

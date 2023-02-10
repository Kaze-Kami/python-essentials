# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

import OpenGL.GL as gl
import glfw
import imgui
import pystray
from PIL import Image
from imgui.integrations.glfw import GlfwRenderer


class AppConfig:
    def __init__(self, width: int, height: int, title: str, icon_path: str, start_minimized: bool = False):
        self.width = width
        self.height = height
        self.title = title
        self.icon_path = icon_path
        self.start_minimized = start_minimized


class App:
    def __init__(self, config: AppConfig):
        self._config = config

        self._icon_image = Image.open(config.icon_path)
        self._window = self._init_glfw(config.width, config.height, config.title, self._icon_image)
        self._imgui_impl = self._init_imgui()
        self._tray_icon = self._init_tray(config.title, self._icon_image)

        self._should_exit = False

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

        # TODO: Maybe initialize application here, instead of in __init__
        if not self._config.start_minimized:
            self._show_window()

        self._should_exit = False
        self._tray_icon.run_detached()

        try:
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

        self.on_stop()
        self._shutdown()

    # noinspection PyMethodMayBeStatic
    def get_additional_tray_actions(self) -> list[pystray.MenuItem]:
        """
        To be overwritten by client to provide additional tray icon actions
        :return: list of additional tray icon actions
        """
        return []

    def _init_glfw(self, width: int, height: int, title: str, icon: Image):
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
                int(width), int(height), title, None, None
        )
        if not window:
            glfw.terminate()
            raise Exception("Could not initialize Window")

        glfw.set_window_iconify_callback(window, self._on_minimize)
        # window icon
        glfw.set_window_icon(window, 1, [icon])

        # init opengl and imgui
        glfw.make_context_current(window)
        return window

    def _init_imgui(self):
        imgui.create_context()
        imgui_impl = GlfwRenderer(self._window)

        # TODO: theme/background color from config
        gl.glClearColor(.1, .1, .1, 1.)

        return imgui_impl

    def _init_tray(self, title, image: Image):
        tray_icon = pystray.Icon(title, image, title, menu=[
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
        imgui.begin('', False,
                    imgui.WINDOW_NO_NAV |
                    imgui.WINDOW_NO_NAV_INPUTS |
                    imgui.WINDOW_NO_MOVE |
                    imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                    imgui.WINDOW_NO_COLLAPSE |
                    imgui.WINDOW_NO_TITLE_BAR)

        self.render()

        imgui.end()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        self._imgui_impl.render(imgui.get_draw_data())
        glfw.swap_buffers(self._window)

    def _on_minimize(self, _, minimized):
        if minimized:
            self.on_hide()
            glfw.hide_window(self._window)

    def _show_window(self, *_):
        glfw.show_window(self._window)
        glfw.restore_window(self._window)
        glfw.focus_window(self._window)
        self.on_show()

    def _stop(self, *_):
        self._should_exit = True

    def _shutdown(self):
        self._imgui_impl.shutdown()
        glfw.terminate()
        self._tray_icon.stop()

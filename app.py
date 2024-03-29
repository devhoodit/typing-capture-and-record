import tkinter
import customtkinter
import win32gui
from pynput import keyboard, mouse
from PIL import ImageGrab
import os
import threading

from typing import List, Dict


class OptionsComponent:
    def __init__(self, app: customtkinter.CTk) -> None:

        self.task_dict = self.load_windows()
        capture_region = ["screen"]

        self.selected_focus = "default"
        self.selected_focus_hwnd = -1
        self.selected_capture_region = "screen"
        self.selected_track_mouse = False
        self.selected_track_keyboard = False

        self.box_focus = customtkinter.CTkComboBox(app, values=list(self.task_dict.keys()), command=self._command_focus)
        self.box_capture_region = customtkinter.CTkComboBox(app, values=capture_region)

        self.check_track_mouse_var = customtkinter.StringVar(value=False)
        self.check_track_keyboard_var = customtkinter.StringVar(value=False)

        self.check_track_mouse_box = customtkinter.CTkCheckBox(app, text="Keyboard", command=self._command_track_mouse, variable=self.check_track_mouse_var, onvalue=True, offvalue=False)
        self.check_track_keyboard_box = customtkinter.CTkCheckBox(app, text="Mouse", command=self._command_track_keyboard, variable=self.check_track_keyboard_var, onvalue=True, offvalue=False)

        self.place()

    def place(self):
        self.box_focus.grid(row=0, column=0, padx=20, pady=10, sticky="ew", columnspan=2)
        self.box_capture_region.grid(row=1, column=0, padx=20, pady=10, sticky="ew", columnspan=2)
        self.check_track_mouse_box.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.check_track_keyboard_box.grid(row=2, column=1, padx=20, pady=10, sticky="w")

    def _command_focus(self, choice):
        self.selected_focus = choice
        self.selected_focus_hwnd = self.task_dict[choice]

    def _command_track_mouse(self):
        self.selected_track_mouse = self.check_track_mouse_var.get()

    def _command_track_keyboard(self):
        self.selected_track_keyboard = self.check_track_keyboard_var.get()

    def load_windows(self) -> Dict:
        def win_enum_handler(hwnd, hwnd_list: Dict):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:
                    hwnd_list[window_title] = hwnd
        hwnd_dict = {"default": -1}
        win32gui.EnumWindows(win_enum_handler, hwnd_dict)
        return hwnd_dict
    
class WindowCapture:
    def __init__(self, hwnd) -> None:
        self.hwnd = hwnd
        self.index = 0
        self.lock = threading.Lock()
        self.directory_check()

    def initialize(self, hwnd):
        self.index = 0
        self.hwnd = hwnd
        self.directory_check()

    def directory_check(self):
        if not os.path.isdir("./images"):
            os.makedirs("./images")

    def capture(self):
        foreground_window_hwnd = win32gui.GetForegroundWindow()
        if foreground_window_hwnd == self.hwnd or -1 == self.hwnd:
            image = ImageGrab.grab()
            self.lock.acquire()
            image.save(f"./images/{self.index}.jpg", format='JPEG', subsampling=0, quality=100)
            self.index += 1
            self.lock.release()

class KeyboardHooker:
    def __init__(self, cap: WindowCapture) -> None:
        self.cap = cap
        self.is_press_enable = True
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def start_hooking(self):
        if not self.listener._thread.is_alive():
            self.listener.join()
        else:
            self.listener.start()
    
    def stop_hooking(self):
        self.listener.stop()

    def on_press(self, _):
        if self.is_press_enable:
            self.is_press_enable = False
            self.cap.capture()

    def on_release(self, _):
        self.is_press_enable = True

class MouseHooker:
    def __init__(self, cap: WindowCapture) -> None:
        self.cap = cap
        self.is_click_enable = True
        self.listener = mouse.Listener(on_click=self.on_click)

    def start_hooking(self):
        if not self.listener._thread.is_alive():
            self.listener.join()
        else:
            self.listener.start()

    def stop_hooking(self):
        self.listener.stop()

    def on_click(self, _, __, ___, pressed):
        if pressed:
            self.cap.capture()

class RecordComponent:
    def __init__(self, app, options: OptionsComponent) -> None:
        self.is_record = False
        self.option_component = options

        # capture
        self.window_capture = WindowCapture(self.option_component.selected_focus_hwnd)

        # hooking
        self.keyboard_hooker = KeyboardHooker(self.window_capture)
        self.mouse_hooker = MouseHooker(self.window_capture)

        self.button = customtkinter.CTkButton(app, text="Record", command=self._command_button, fg_color="#00fa4f")
        self.place()

    def place(self):
        self.button.grid(row=3, column=0, padx=20, pady=10, sticky='ew', columnspan=2)

    def _command_button(self):
        # go here
        self.is_record = not self.is_record
        if self.is_record:
            self.button.configure(fg_color="#fa0047")
            self.window_capture.initialize(self.option_component.selected_focus_hwnd)
            if self.option_component.check_track_keyboard_var:
                self.keyboard_hooker.start_hooking()
            if self.option_component.check_track_mouse_var:
                self.mouse_hooker.start_hooking()

        else:
            self.button.configure(fg_color="#00fa4f")
            try:
                self.keyboard_hooker.stop_hooking()
            finally:
                pass
            try:
                self.mouse_hooker.stop_hooking()
            finally:
                pass

class ConvertComponent:
    def __init__(self, app) -> None:
        self.button = customtkinter.CTkButton(app, text="Convert", command=self._command_button)
        self.place()

    def place(self):
        self.button.grid(row=4, column=0, padx=20, pady=10, sticky='ew', columnspan=2)

    def _command_button(self):
        os.system('ffmpeg -r 60 -i "./images/%d.jpg" -vcodec mpeg4 -s 1920x1080 -b 9000k -y output.mp4')

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x280")
        self.title("Capture & Record v0.0.2")
        self.grid_columnconfigure((0), weight=1)

        # Widgets go
        self.option_component = OptionsComponent(self)
        self.record_component = RecordComponent(self, self.option_component)
        self.convert_component = ConvertComponent(self)

app = App()
app.mainloop()
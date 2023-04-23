import tkinter
import customtkinter
import win32gui
from pynput import keyboard, mouse

from typing import List, Dict


class OptionsComponent:
    def __init__(self, app: customtkinter.CTk) -> None:

        task_dict = self.load_windows()
        capture_region = ["screen"]

        self.selected_focus = "default"
        self.selected_capture_region = "screen"
        self.selected_track_mouse = False
        self.selected_track_keyboard = False

        self.box_focus = customtkinter.CTkComboBox(app, values=list(task_dict.keys()), command=self._command_focus)
        self.box_capture_region = customtkinter.CTkComboBox(app, values=capture_region)

        self.check_track_mouse_var = customtkinter.StringVar(value=False)
        self.check_track_keyboard_var = customtkinter.StringVar(value=True)

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
    
class Capture:
    def __init__(self) -> None:
        pass

class RecordComponent:
    def __init__(self, app, options: OptionsComponent) -> None:
        pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x280")
        self.title("Capture & Record")
        self.grid_columnconfigure((0), weight=1)

        # Widgets go
        self.option_component = OptionsComponent(self)

app = App()
app.mainloop()
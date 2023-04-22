from PIL import ImageGrab
import win32gui
from pynput import keyboard

def win_enum_handler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title:
            print(f"{hwnd}\t|   {window_title}")

win32gui.EnumWindows(win_enum_handler, None)

class WindowCapture:
    def __init__(self, hwnd) -> None:
        self.hwnd = hwnd
        self.index = 0
    
    def capture(self):
        foreground_window_hwnd = win32gui.GetForegroundWindow()
        if foreground_window_hwnd == self.hwnd:
            image = ImageGrab.grab()
            image.save(f"./images/{self.index}.jpg", format='JPEG', subsampling=0, quality=100)
            self.index += 1


class KeyboardHooker:
    def __init__(self, cap: WindowCapture) -> None:
        self.cap = cap
        self.is_press_enable = True

    def on_press(self, key):
        if self.is_press_enable:
            self.is_press_enable = False
            self.cap.capture()

    def on_release(self, key):
        self.is_press_enable = True

hwnd = int(input("which? :"))
window_capture = WindowCapture(hwnd)
keyboard_hooker = KeyboardHooker(window_capture)

with keyboard.Listener(on_press=keyboard_hooker.on_press, on_release=keyboard_hooker.on_release) as k_listener:
    k_listener.join()
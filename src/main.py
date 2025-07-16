# * Library imports
import sys
import asyncio
import flet as ft
import PySpin
import matplotlib

# Import the UI page from the package
from .pages import HomePage

if sys.platform == 'darwin':
    matplotlib.use('MacOSX')
else:
    matplotlib.use('TkAgg')

class Camera:
    def __init__(self):
        self.system: any = PySpin.System.GetInstance()
        self.camera_list: any = self.system.GetCameras()
        self.camera: any = self.camera_list.GetByIndex(0) if self.camera_list.GetSize() > 0 else None
        self.dev_mode: bool = False
        self.title = "DINCIP Thermal Imager"
        self.theme_mode = ft.ThemeMode.DARK
        self.page = None
        self.terminal_textbox = None

    def log_to_terminal(self, message):
        if self.terminal_textbox and self.page:
            current_text = self.terminal_textbox.value or ""
            self.terminal_textbox.value = current_text + "\n" + "$ " + message
            self.page.update()

    async def main(self, page: ft.Page):
        num_cameras = self.camera_list.GetSize()

        home_page = HomePage(self)

        await home_page.setup_page(page)

        self.log_to_terminal(f"Cameras detected: {num_cameras}")

async def main():
    camera = Camera()
    await ft.app_async(target=camera.main, view=ft.AppView.FLET_APP)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting program")
    except Exception as e:
        print(f"Application error: {e}")
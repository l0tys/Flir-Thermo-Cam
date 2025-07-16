# * Library imports
import flet as ft

from components import TerminalComponent

class HomePage:
    def __init__(self, camera_instance):
        self.camera = camera_instance

    def create_image_control(self):
        return ft.Container(
            width=640,
            height=480,
            bgcolor=ft.Colors.BLACK54
        )

    def create_main_layout(self):
        image_control = self.create_image_control()
        terminal_container = TerminalComponent.create_terminal_container()

        return ft.SafeArea(
            ft.Row([
                ft.Column([
                    ft.Container(
                        content=image_control,
                        alignment=ft.alignment.center_left,
                        border_radius=10,
                        padding=10
                    ),
                    ft.Text("Thermal Imager Terminal", size=16),
                    terminal_container
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),

                ft.Column([
                ], expand=True)
            ], expand=True)
        )

    async def setup_page(self, page: ft.Page):
        page.title = self.camera.title
        page.theme_mode = self.camera.theme_mode

        self.camera.page = page
        self.camera.terminal_textbox = self.terminal_textbox

        try:
            main_layout = self.create_main_layout()
            page.add(main_layout)

            page.update()

        except Exception as e:
            print(f"Error: {e}")
            self.camera.log_to_terminal(f"$ ERROR: {e}")
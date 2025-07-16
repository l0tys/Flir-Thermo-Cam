# * Library imports
import flet as ft


class TerminalComponent:
    def __init__(self):
        self.terminal_textbox = None

    def create_terminal_textbox(self):
        self.terminal_textbox = ft.TextField(
            value="$ DINCIP Thermal Imager Terminal",
            multiline=True,
            min_lines=12,
            max_lines=20,
            text_style=ft.TextStyle(
                font_family="Consolas, Monaco, monospace",
                size=12,
                color=ft.Colors.GREEN_400
            ),
            bgcolor=ft.Colors.BLACK,
            border_color=ft.Colors.GREY_700,
            hint_text="System logs will appear here...",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
            read_only=True,
            expand=True
        )
        return self.terminal_textbox

    def create_terminal_container(self):
        terminal_textbox = self.create_terminal_textbox()

        return ft.Container(
            content=terminal_textbox,
            bgcolor=ft.Colors.BLACK,
            border=ft.border.all(1, ft.Colors.GREY_700),
            border_radius=5,
            padding=5,
            width=650,
            height=140
        )
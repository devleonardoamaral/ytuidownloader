import os
from pathlib import Path
from threading import Thread

from donwloader import DownloadInfo, Link, YoutubeDownloader
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.validation import Validator
from textual.widgets import Button, Footer, Header, Input, Label, ProgressBar


class TUIApp(App):
    def __init__(self, downloader: YoutubeDownloader, input_validator: Validator):
        super().__init__()
        self.downloader = downloader
        self.input_validator = input_validator
        self.download_thread: Thread | None = None
        self.input_link = Input(
            type="text",
            placeholder="Link de download (video, canal, playlist) ...",
            id="input_link",
            validators=self.input_validator,
        )
        self.button_download = Button("Download", id="button_download", disabled=True)
        self.progress_bar = ProgressBar()
        self.label = Label("")
        self.title = "Youtube Downloader"
        self.history = []

    def compose(self) -> ComposeResult:
        self.input_link.styles.width = self.screen.size.width * 0.75
        self.input_link.styles.max_width = 75

        self.progress_bar.styles.width = self.screen.size.width // 2
        self.progress_bar.styles.align = ("center", "middle")
        self.progress_bar.styles.height = 3

        horizontal_1 = Horizontal(self.input_link, self.button_download)
        horizontal_1.styles.align = ("center", "bottom")

        horizontal_2 = Horizontal(self.label)
        horizontal_2.styles.align = ("center", "middle")
        horizontal_2.styles.height = 3

        horizontal_3 = Horizontal(self.progress_bar)
        horizontal_3.styles.align = ("center", "top")

        vertical = Vertical(horizontal_1, horizontal_2, horizontal_3)

        yield Header()
        yield vertical
        yield Footer()

    def progress_hook(self, downloaded: int, total: int | None) -> None:
        if not self.progress_bar.total or self.progress_bar.total != total:
            self.progress_bar.update(total=total, progress=downloaded)
        else:
            new_value = downloaded - self.progress_bar.progress
            self.progress_bar.advance(new_value)

    def join_hook(self, info: DownloadInfo, error: Exception | None) -> None:
        if info.downloaded:
            if self.progress_bar.total is None:
                self.label.update("Essa URL já foi baixada anteriormente.")
            else:
                self.label.update("Download Concluído!")
                self.button_download.disabled = False
        else:
            self.label.update(f"Falha no Download: {str(error)}")

        self.thread = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_download":
            if self.download_thread is None or not self.download_thread.is_alive():
                self.button_download.disabled = True
                self.download_thread = self.downloader.download(
                    Link(self.input_link.value),
                    Path(os.getcwd()),
                    progress_hook=self.progress_hook,
                    join_hook=self.join_hook,
                )
                self.label.update("Baixando...")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "input_link":
            self.button_download.disabled = True

            if self.download_thread is None or not self.download_thread.is_alive():
                self.progress_bar.total = None

                if self.input_link.is_valid:
                    self.label.update("Pressione o botão para começar...")
                    self.button_download.disabled = False
                else:
                    self.label.update("Link inválido!")

from pathlib import Path
from threading import Thread

from donwloader import DownloadInfo, Link, YoutubeDownloader
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.validation import Validator
from textual.widgets import Button, Footer, Header, Input, Label, ProgressBar


class TUIApp(App):
    def __init__(
        self,
        downloader: YoutubeDownloader,
        input_link_validator: Validator,
        input_path_validator: Validator,
    ):
        super().__init__()
        self.downloader = downloader
        self.input_link_validator = input_link_validator
        self.input_path_validator = input_path_validator
        self.download_thread: Thread | None = None
        self.title = "Youtube Downloader"
        self.history = []

    def compose(self) -> ComposeResult:
        self.input_link = Input(
            type="text",
            placeholder="Paste here the YouTube link (video, channel, playlist)...",
            id="input_link",
            validators=self.input_link_validator,
        )
        self.input_link.styles.align = ("center", "middle")
        self.input_link.styles.content_align = ("center", "middle")
        self.input_link.styles.width = 75
        self.input_link.styles.height = 3
        self.input_link.border_title = "Link:"
        input_link_horizontal = Horizontal(self.input_link)
        input_link_horizontal.styles.align = ("center", "middle")
        input_link_horizontal.styles.height = 5
        input_link_horizontal.styles.width = 75

        self.input_path = Input(
            type="text",
            placeholder="Paste here the directory where the video will be saved...",
            id="input_path",
            validators=self.input_path_validator,
            valid_empty=True,
        )
        self.input_path.styles.align = ("center", "middle")
        self.input_path.styles.content_align = ("center", "middle")
        self.input_path.styles.width = 75
        self.input_path.styles.height = 3
        self.input_path.border_title = "Download Directory:"
        input_path_horizontal = Horizontal(self.input_path)
        input_path_horizontal.styles.align = ("center", "middle")
        input_path_horizontal.styles.height = 5
        input_path_horizontal.styles.width = 75

        self.button_download = Button("Download", id="button_download", disabled=True)
        self.button_download.styles.align = ("center", "middle")
        self.button_download.styles.width = 75 // 2
        button_horizontal = Horizontal(self.button_download)
        button_horizontal.styles.align = ("center", "middle")
        button_horizontal.styles.height = 5
        button_horizontal.styles.width = 75

        self.label = Label("Hello, wellcome!")
        self.label.styles.align = ("center", "middle")
        self.label.styles.content_align = ("center", "middle")
        self.label.styles.width = 75
        self.label.styles.height = 3

        self.progress_bar = ProgressBar()
        self.progress_bar.styles.align = ("center", "middle")
        self.progress_bar.styles.height = 3
        self.progress_bar.styles.width = 75

        vertical = Vertical(
            input_link_horizontal,
            input_path_horizontal,
            self.progress_bar,
            self.label,
            button_horizontal,
        )

        vertical.styles.align = ("center", "middle")

        yield Header()
        yield vertical
        yield Footer()

    def _is_download_thread_running(self) -> bool:
        return self.download_thread is not None and self.download_thread.is_alive()

    def _update_download_button(self) -> None:
        self.button_download.disabled = not (
            self.input_link.is_valid
            and self.input_path.is_valid
            and not self._is_download_thread_running()
        )

    def progress_hook(self, downloaded: int, total: int | None) -> None:
        if not self.progress_bar.total or self.progress_bar.total != total:
            self.progress_bar.update(total=total, progress=downloaded)
        else:
            new_value = downloaded - self.progress_bar.progress
            self.progress_bar.advance(new_value)

    def join_hook(self, info: DownloadInfo, error: Exception | None) -> None:
        if info.downloaded:
            self.label.update("Download completed")
        else:
            self.label.update(f"Download failed: {str(error)}")
        self.progress_hook(100, 100)
        self.thread = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_download":
            if not self._is_download_thread_running():
                self.download_thread = self.downloader.download(
                    Link(self.input_link.value),
                    Path(self.input_path.value),
                    progress_hook=self.progress_hook,
                    join_hook=self.join_hook,
                )
                self._update_download_button()
                self.label.update("Downloading...")

    def on_input_changed(self, event: Input.Changed) -> None:
        if self.input_link.is_valid and self.input_path.is_valid:
            self.label.update("Press the Download button to start...")
        elif not self.input_link.is_valid:
            self.label.update("Invalid link")
        elif not self.input_path.is_valid:
            self.label.update("Invalid path")

        if not self._is_download_thread_running():
            self.progress_bar.total = None
        self._update_download_button()

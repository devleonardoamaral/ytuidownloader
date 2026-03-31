from dataclasses import dataclass
from functools import partial
from pathlib import Path
from threading import Thread
from typing import Callable

import yt_dlp


@dataclass
class Link:
    value: str

    def __str__(self) -> str:
        return self.value

    def __post_init__(self) -> None:
        self.value = self.value.strip()

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Link):
            return False
        elif self.value == value.value:
            return True
        else:
            return False


@dataclass
class DownloadInfo:
    title: str
    extension: str
    url: Link
    downloaded: bool

    def filename(self) -> str:
        return self.extension and f"{self.title}.{self.extension}" or self.title


class YoutubeDownloader:
    def progress_hook(
        self,
        func: Callable[[int, int | None], None],
        progress_data: dict,
    ) -> None:
        downloaded = progress_data.get("downloaded_bytes", 0)
        total = progress_data.get("total_bytes", None)
        func(downloaded, total)

    def thread_task(
        self,
        url: Link,
        output_dir: Path,
        progress_hook: Callable[[int, int | None], None] | None = None,
        join_hook: Callable[[DownloadInfo, Exception | None], None] | None = None,
    ) -> None:
        url_info = None
        download_info = DownloadInfo(title="", extension="", url=url, downloaded=False)
        error = None

        params: yt_dlp._Params = {
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "format": "bv+ba/b",
            "noplaylist": not ("playlist" in url.value or "channel" in url.value),
        }

        try:
            with yt_dlp.YoutubeDL(params) as ydl:
                if progress_hook is not None:
                    progress_hook_wrapper = partial(self.progress_hook, progress_hook)
                    ydl.add_progress_hook(progress_hook_wrapper)
                url_info = ydl.extract_info(url.value)
                download_info.title = str(url_info.get("title", "UnknownVideoName"))
                download_info.extension = str(url_info.get("ext", ""))
                download_info.downloaded = True
        except Exception as e:
            error = e
        finally:
            if join_hook is not None:
                join_hook(download_info, error or None)

    def download(
        self,
        url: Link,
        output_dir: Path,
        progress_hook: Callable[[int, int | None], None] | None = None,
        join_hook: Callable[[DownloadInfo, Exception | None], None] | None = None,
    ) -> Thread:
        """Download an Youtube video."""

        thread = Thread(
            target=self.thread_task,
            kwargs={
                "url": url,
                "output_dir": output_dir,
                "progress_hook": progress_hook,
                "join_hook": join_hook,
            },
        )

        thread.start()
        return thread

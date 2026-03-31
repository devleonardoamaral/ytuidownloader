import os
from pathlib import Path

from donwloader import YoutubeDownloader
from tui import TUIApp
from tui.validators import YoutubeValidator


def main() -> None:
    output_dir = Path(os.getcwd())

    try:
        output_dir.mkdir(exist_ok=True)
    except Exception as e:
        raise RuntimeError("Could not create download directory.") from e

    youtube_validator = YoutubeValidator()
    yt_downloader = YoutubeDownloader()
    app = TUIApp(downloader=yt_downloader, input_validator=youtube_validator)
    app.run()


if __name__ == "__main__":
    main()

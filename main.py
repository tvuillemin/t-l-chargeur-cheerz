import json
from argparse import ArgumentParser
from asyncio import Task, create_task, run, wait
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from itertools import chain, islice
from os import makedirs
from typing import Any, Dict, List
from urllib.request import urlopen, urlretrieve


class CheezPageParser(HTMLParser):
    SCRIPT_START = "var galleriesBundleData = "

    def __init__(self) -> None:
        super().__init__()
        self.inside_script = False
        self.photos_dict: Dict[str, Any] = {}

    def handle_starttag(self, tag: str, _: Any) -> None:
        if tag == "script":
            self.inside_script = True

    def handle_data(self, data: str) -> None:
        if self.inside_script:
            if data.startswith(self.SCRIPT_START):
                self.photos_dict = json.loads(data.replace(self.SCRIPT_START, ""))


@dataclass(frozen=True)
class Photo:
    taken_at: datetime
    url: str
    original_url: str

    @classmethod
    def from_dict(cls, photo_dict: Dict[str, Any]):
        return cls(
            taken_at=photo_dict["taken_at"],
            url=photo_dict["url"],
            original_url=photo_dict["original_url"],
        )

    def get_download_tasks(self) -> List[Task]:
        makedirs("photos/originales", exist_ok=True)
        makedirs("photos/filtrées", exist_ok=True)
        return [
            create_task(self._download_original()),
            create_task(self._download_filtered()),
        ]

    async def _download_original(self) -> None:
        urlretrieve(self.original_url, f"photos/originales/{self.taken_at}")

    async def _download_filtered(self) -> None:
        urlretrieve(self.original_url, f"photos/filtrées/{self.taken_at}")


async def main() -> None:
    # Parse the command line arguments
    args_parser = ArgumentParser(description="Télécharger des photos Cheerz")
    args_parser.add_argument("url", help="L'URL de la galerie")
    args = args_parser.parse_args()

    # Download the Cheerz page
    cheerz_page = urlopen(args.url).read().decode()

    # Parse the Cheerz page content
    html_parser = CheezPageParser()
    html_parser.feed(cheerz_page)
    photos = (Photo.from_dict(d) for d in html_parser.photos_dict["photoData"])

    # Create and wait for all the download tasks
    await wait(chain.from_iterable(p.get_download_tasks() for p in photos))


if __name__ == "__main__":
    run(main())

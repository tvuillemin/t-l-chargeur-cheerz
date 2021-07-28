import json
from asyncio import Task, create_task, run, wait
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from itertools import chain
from os import makedirs
from typing import Any, Dict, List
from urllib.request import urlopen, urlretrieve

URL = "https://live.cheerz.com/galleries/7J1U8-c4576350ecf2d22b47ff4e6e7d2fee0d37f1e5f5"


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
    # Download the Cheerz page
    cheerz_page = urlopen(URL).read().decode()

    # Parse the Cheerz page content
    parser = CheezPageParser()
    parser.feed(cheerz_page)
    photos = (Photo.from_dict(d) for d in parser.photos_dict["photoData"])

    # Create and wait for all the download tasks
    await wait(chain.from_iterable(p.get_download_tasks() for p in photos))


if __name__ == "__main__":
    run(main())

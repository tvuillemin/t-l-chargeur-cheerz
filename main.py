import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from os import makedirs
from typing import Any, List, Mapping
from urllib.request import urlopen, urlretrieve

from bs4 import BeautifulSoup

URL = "https://live.cheerz.com/galleries/7J1U8-c4576350ecf2d22b47ff4e6e7d2fee0d37f1e5f5"


@dataclass(frozen=True)
class Photo:
    taken_at: datetime
    url: str
    original_url: str

    @classmethod
    def from_dict(cls, photo_dict: Mapping[str, Any]):
        return cls(
            taken_at=photo_dict["taken_at"],
            url=photo_dict["url"],
            original_url=photo_dict["original_url"],
        )

    async def download_original(self) -> None:
        self._create_folders()
        urlretrieve(self.original_url, f"photos/originales/{self.taken_at}")

    async def download_filtered(self) -> None:
        self._create_folders()
        urlretrieve(self.original_url, f"photos/filtrées/{self.taken_at}")

    @staticmethod
    def _create_folders():
        makedirs("photos/originales", exist_ok=True)
        makedirs("photos/filtrées", exist_ok=True)


async def main() -> None:
    cheerz_page = urlopen(URL).read()
    photo_script = next(
        BeautifulSoup(cheerz_page, "html.parser").find_all("script")[2].children
    )
    json_start = photo_script.find("{")
    photos_dict = json.loads(str(photo_script[json_start:]))

    photos = [Photo.from_dict(d) for d in photos_dict["photoData"]]

    tasks: List[asyncio.Task] = []
    for photo in photos:
        tasks.extend(
            [
                asyncio.create_task(photo.download_original()),
                asyncio.create_task(photo.download_filtered()),
            ]
        )

    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Mapping

import requests
from bs4 import BeautifulSoup

URL = "https://live.cheerz.com/galleries/7J1U8-c4576350ecf2d22b47ff4e6e7d2fee0d37f1e5f5"


@dataclass(frozen=True)
class PhotoReference:
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


async def main() -> None:
    cheerz_page = requests.get(URL)
    photo_script = next(
        BeautifulSoup(cheerz_page.text, "html.parser").find_all("script")[2].children
    )
    json_start = photo_script.find("{")
    photos_dict = json.loads(str(photo_script[json_start:]))

    photo_references = [PhotoReference.from_dict(d) for d in photos_dict["photoData"]]

    tasks: List[asyncio.Task] = []
    for ref in photo_references:
        tasks.extend(
            [
                asyncio.create_task(download_original_photo(ref)),
                asyncio.create_task(download_filtered_photo(ref)),
            ]
        )

    await asyncio.wait(tasks)


async def download_original_photo(ref: PhotoReference) -> None:
    with open(f"photos/originales/{ref.taken_at}", "wb") as originale:
        response = requests.get(ref.original_url, allow_redirects=True)
        originale.write(response.content)


async def download_filtered_photo(ref: PhotoReference) -> None:
    with open(f"photos/filtres/{ref.taken_at}", "wb") as filtre:
        response = requests.get(ref.url, allow_redirects=True)
        filtre.write(response.content)


if __name__ == "__main__":
    asyncio.run(main())

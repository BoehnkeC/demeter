from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse
from urllib.request import urlretrieve

import pystac
from pystac_client import Client

from utils import strip_scene_name, alter_date, get_closest_date

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class DataRetrieval:
    """Encapsulate data retrieval."""

    def __init__(self: DataRetrieval, aoi: tuple, out_dir: Path, start_date: str, end_date: str) -> None:
        """Initialize DataRetrieval class."""
        self.aoi = aoi
        self.out_dir = out_dir
        self.out_scene = None
        self.out_name = None
        self.items = None
        self.start_date = start_date
        self.end_date = end_date
        self.altered_start_date = None
        self.altered_end_date = None

    def __enter__(self: DataRetrieval) -> DataRetrieval:
        """Get opening handler on context manager."""
        return self

    def __exit__(
        self: DataRetrieval,
        exc_type: type(BaseException),
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        """Get closing handler on context manager."""
        self.close()

    def close(self: DataRetrieval) -> None:
        """Close this class."""
        del self.items

    def check_out_dir(self: DataRetrieval, scene: str, event: str) -> Path:
        """Create output directory if not existing."""
        out_scene = self.out_dir.joinpath(f"{strip_scene_name(data=scene)}_{event}")

        if not out_scene.exists():
            out_scene.mkdir(parents=True)

        return out_scene

    @staticmethod
    def build_out_name(href: str) -> str:
        """Build the output filename."""
        return "_".join(urlparse(href).path.split("/")[-2:])  # get path of URL, re-join last two items

    def download_band(self: DataRetrieval, item: pystac.Item, out_scene: Path) -> None:
        """Download a specific band."""
        for band in ["nir", "swir22"]:
            out_name = self.build_out_name(href=item.assets[f"{band}"].href)
            urlretrieve(item.assets[f"{band}"].href, out_scene.joinpath(out_name))

    def connect_to_stac(self: DataRetrieval) -> None:
        """Establish a connection to STAC catalog."""
        aws_stac = Client.open("https://earth-search.aws.element84.com/v1")
        search = aws_stac.search(
            collections="sentinel-2-l2a",
            bbox=self.aoi,
            datetime=f"{self.altered_start_date}/{self.altered_end_date}",
        )
        self.items = list(search.items())

    def check_items(self: DataRetrieval, required_data: int = 2) -> None:
        """Check if STAC list contains at least 2 elements."""
        if len(self.items) < required_data:
            raise AttributeError(
                f"Insufficient number of data retrieved, minimum requirement: 2, retrieved: {len(self.items)}."
            )

    def alter_dates(self):
        """Substract and add 10 days to start and end date to fully cover the desired time range."""
        self.altered_start_date = alter_date(self.start_date, operator="-")
        self.altered_end_date = alter_date(self.end_date, operator="+")

    def get_data(self: DataRetrieval) -> None:
        """Search and download data."""
        self.alter_dates()
        self.connect_to_stac()
        self.check_items()

        for item in self.items:
            if get_closest_date(date_list=self.items, date=self.start_date, start=True) in item.id:
                out_scene = self.check_out_dir(scene=item.id, event="pre")

            elif get_closest_date(date_list=self.items, date=self.end_date, start=False) in item.id:
                out_scene = self.check_out_dir(scene=item.id, event="post")

            else:
                continue

            self.download_band(item=item, out_scene=out_scene)

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse
from urllib.request import urlretrieve

from pystac_client import Client

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class DataRetrieval:
    """Encapsulate data retrieval."""

    def __init__(self: DataRetrieval, aoi: tuple, out_dir: Path, start_date: str, end_date: str, cloud_cover: float = 1.0) -> None:
        """Initialize DataRetrieval class."""
        self.aoi = aoi
        self.out_dir = out_dir
        self.out_scene = None
        self.out_name = None
        self.items = None
        self.start_date = start_date
        self.end_date = end_date
        self.cloud_cover = cloud_cover

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
        out_scene = self.out_dir.joinpath(f"{scene}_{event}")

        if not out_scene.exists():
            out_scene.mkdir(parents=True)

        return out_scene

    @staticmethod
    def build_out_name(href: str) -> str:
        """Build the output filename."""
        return "_".join(urlparse(href).path.split("/")[-2:])  # get path of URL, re-join last two items

    @staticmethod
    def download_band(href: str, out_scene: Path, out_name: str) -> None:
        """Download a specific band."""
        urlretrieve(href, out_scene.joinpath(out_name))

    def connect_to_stac(self: DataRetrieval) -> None:
        """Establish a connection to STAC catalog."""
        aws_stac = Client.open("https://earth-search.aws.element84.com/v1")
        search = aws_stac.search(
            collections="sentinel-2-l2a",
            bbox=self.aoi,
            datetime=f"{self.start_date}/{self.end_date}",
            query={"eo:cloud_cover": {"lt": self.cloud_cover}},
        )
        self.items = list(search.items())

    def check_items(self: DataRetrieval, required_data: int = 2) -> None:
        """Check if STAC list contains at least 2 elements."""
        if len(self.items) < required_data:
            raise AttributeError(f"Insufficient number of data retrieved, minimum requirement: 2, retrieved: {len(self.items)}.")

    def get_data(self: DataRetrieval) -> None:
        """Search and download data."""
        item_indices = {  # define indices in items list
            "pre": -1,
            "post": 0
        }

        self.connect_to_stac()
        self.check_items()

        for event in item_indices:
            item = self.items[item_indices[event]]  # pre-event has item index -1, post-event has index 0
            out_scene = self.check_out_dir(scene=item.id, event=event)
            for band in ["nir08", "swir22"]:
                out_name = self.build_out_name(href=item.assets[f"{band}"].href)
                self.download_band(href=item.assets[f"{band}"].href, out_scene=out_scene, out_name=out_name)

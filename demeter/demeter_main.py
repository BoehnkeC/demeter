from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from . import aoi_check
from . import burnt_area_mapper
from . import data_retrieval

if TYPE_CHECKING:
    from types import TracebackType


class Demeter:
    """Encapsulate main methodology."""

    def __init__(self: Demeter, in_dir: str, out_dir: str, start_date: str = "2023-01-01", end_date: str = "2023-01-10", cloud_cover: float = 1.0) -> None:
        """Initialize Demeter class."""
        self.aoi = None
        self.in_dir = Path(in_dir)
        self.out_dir = Path(out_dir)
        self.out_scene = None
        self.out_name = None
        self.items = None
        self.start_date = start_date
        self.end_date = end_date
        self.cloud_cover = cloud_cover

    def __enter__(self: Demeter) -> Demeter:
        """Get opening handler on context manager."""
        return self

    def __exit__(
        self: Demeter,
        exc_type: type(BaseException),
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        """Get closing handler on context manager."""

    def execute(self: Demeter, aoi: str | None = None) -> None:
        """Execute main method calling all other methods."""
        with aoi_check.AOI(data_dir=self.in_dir, data=aoi) as aoi:
            self.aoi = aoi.geometry

            with data_retrieval.DataRetrieval(aoi=self.aoi, out_dir=self.out_dir, start_date=self.start_date, end_date=self.end_date, cloud_cover=self.cloud_cover) as _data:
                _data.get_data()

            with burnt_area_mapper.BurntAreaMapper(out_dir=self.out_dir, aoi=self.aoi) as bam:
                bam.get_burnt_area()

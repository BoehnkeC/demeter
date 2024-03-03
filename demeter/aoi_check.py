from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import TracebackType

from pathlib import Path

import fiona
from shapely import from_wkt
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon


class AOI:
    """Encapsulate input operations."""

    def __init__(self: AOI, data_dir: Path, data: str | Path | Polygon) -> None:
        """Initialize AOI class."""
        self.geometry = None
        self.aoi = None
        self.features = None

        if isinstance(data, str):
            if "POLYGON" in data:  # wkt string
                self.geometry = from_wkt(data).bounds

            elif data_dir.joinpath(data).exists():
                self.filename = data_dir.joinpath(data)
                self.load_aoi()
                self.get_feature()

            else:
                raise TypeError(f"The provided data {data} cannot be resolved to WKT or to a path.")

        elif isinstance(data_dir.joinpath(data), Path):
            self.filename = data_dir.joinpath(data)
            self.load_aoi()
            self.get_feature()

        elif isinstance(data, Polygon):
            self.geometry = data.bounds

        else:
            raise TypeError(f"The provided data {data} is of unsupported type {type(data)}.")

    def __enter__(self: AOI) -> AOI:
        """Get opening handler on context manager."""
        return self

    def __exit__(
        self: AOI,
        exc_type: type(BaseException),
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        """Get closing handler on context manager."""
        self.close()

    def close(self: AOI) -> None:
        """Clode AOI file."""
        if self.aoi is not None:
            self.aoi.close()

    def load_aoi(self: AOI) -> None:
        """Open AOI file."""
        self.aoi = fiona.open(self.filename)

    def get_features(self: AOI) -> None:
        """Get features from opened AOI instance."""
        self.features = list(self.aoi)

    def get_feature(self: AOI) -> None:
        """Get AOI feature and its geometry."""
        self.get_features()

        if self.geometry is None and len(self.features) == 1:
            self.geometry = shape(self.features[0].geometry).bounds

        elif self.geometry is None and len(self.features) > 1:
            self.geometry = MultiPolygon([shape(feature["geometry"]) for feature in self.features]).bounds

        else:
            raise AttributeError(f"The AOI {self.filename} does not contain any features.")

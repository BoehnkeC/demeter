from __future__ import annotations

from typing import TYPE_CHECKING

from ukis_pysat.raster import Image

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class Event:
    """Encapsulate methods for Event class."""

    def __init__(self: Event, data_dir: Path, aoi: tuple, event: str = "pre") -> None:
        """Initialize Event class."""
        self.data_dir = data_dir
        self.aoi = aoi
        self.event = event
        self.nir = None
        self.swir = None
        self.nbr = None

        self.update_data_dir()

    def __enter__(self: Event) -> Event:
        """Get opening handler on context manager."""
        return self

    def __exit__(
            self: Event,
            exc_type: type(BaseException),
            exc_val: BaseException,
            exc_tb: TracebackType,
    ) -> None:
        """Get closing handler on context manager."""
        self.nir.close()
        self.swir.close()

    def update_data_dir(self: Event) -> None:
        """Update the data directory."""
        self.data_dir = next(iter(self.data_dir.glob(f"*_{self.event}")))  # attach 'pre' or 'post'

    def get_nir_file(self: Event) -> Path:
        """Get file path of NIR band."""
        return next(iter(self.data_dir.glob("*B8A.tif")))

    def get_swir_file(self: Event) -> Path:
        """Get file path of SWIR band."""
        return next(iter(self.data_dir.glob("*B12.tif")))

    def get_rasters(self: Event) -> None:
        """Open NIR and SWIR raster files."""
        self.nir = Image(data=self.get_nir_file())
        self.swir = Image(data=self.get_swir_file())

    def crop_rasters(self: Event) -> None:
        """Crop NIR and SWIR rasters to the extent of the AOI."""
        self.nir.mask(bbox=self.aoi, crop=True)
        self.swir.mask(bbox=self.aoi, crop=True)

    def get_normalized_burnt_ratio(self: Event) -> None:
        """Get the normalized burnt ratio for this specific event."""
        self.get_rasters()
        # self.crop_rasters()
        nbr = (self.nir.arr - self.swir.arr) / (self.nir.arr + self.swir.arr)  # compute NBR
        self.nbr = Image(data=nbr, crs=self.nir.dataset.crs, transform=self.nir.dataset.transform, nodata=self.nir.dataset.nodata)


class BurntAreaMapper:
    """Encapsulates methods for BurntAreaMapper class."""

    def __init__(self: BurntAreaMapper, out_dir: Path, aoi: tuple) -> None:
        """Initialize BurntAreaMapper class."""
        self.out_dir = out_dir
        self.aoi = aoi
        self.dnbr = None
        self.nbr = None

    def __enter__(self: BurntAreaMapper) -> BurntAreaMapper:
        """Get opening handler on context manager."""
        return self

    def __exit__(
            self: BurntAreaMapper,
            exc_type: type(BaseException),
            exc_val: BaseException,
            exc_tb: TracebackType,
    ) -> None:
        """Get closing handler on context manager."""
        self.dnbr.close()

    def get_burnt_area(self: BurntAreaMapper) -> None:
        """Compute the burnt area."""
        with Event(data_dir=self.out_dir, event="pre", aoi=self.aoi) as pre_event:
            pre_event.get_normalized_burnt_ratio()

            with Event(data_dir=self.out_dir, event="post", aoi=self.aoi) as post_event:
                post_event.get_normalized_burnt_ratio()
                self.get_normalized_burnt_ratio_difference(nbr_pre=pre_event.nbr, nbr_post=post_event.nbr)

    def get_normalized_burnt_ratio_difference(self: BurntAreaMapper, nbr_pre: Image, nbr_post: Image) -> None:
        """Compute the difference of the pre-event NBR and the post-event NBR."""
        dnbr = nbr_pre.arr - nbr_post.arr
        self.dnbr = Image(data=dnbr, crs=nbr_pre.dataset.crs, transform=nbr_pre.dataset.transform, nodata=nbr_pre.dataset.nodata)
        self.dnbr.write_to_file(path_to_file=self.out_dir.joinpath("dnbr.tif"), dtype=nbr_pre.arr.dtype, nodata=nbr_pre.dataset.nodata, compress="lzw")

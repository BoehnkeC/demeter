from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from rasterio.crs import CRS
from rasterio.merge import merge
from ukis_pysat.raster import Image

from utils import strip_scene_name

if TYPE_CHECKING:
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

    def get_nir_file(self: Event, required_data: int = 1) -> Path:
        """Get file path of NIR band."""
        if len(list(self.data_dir.glob("*B08.tif"))) > required_data:  # multiple tiles from same overpass, merge those
            return self.merge_tiles(files=list(self.data_dir.glob("*B08.tif")))

        else:  # only one NIR tile found
            return next(iter(self.data_dir.glob("*B08.tif")))

    def get_swir_file(self: Event, required_data: int = 1) -> Path:
        """Get file path of SWIR band."""
        if len(list(self.data_dir.glob("*B12.tif"))) > required_data:  # multiple tiles from same overpass, merge those
            return self.merge_tiles(files=list(self.data_dir.glob("*B12.tif")))

        else:  # only one SWIR tile found
            return next(iter(self.data_dir.glob("*B12.tif")))

    def merge_tiles(self: Event, files: list) -> Path:
        """Merge Sentinel-2 input tiles."""
        # files = sorted(files, key=lambda item: item.name)  # sort file paths
        img_list = [
            self.reproject_input(item).dataset for item in files
        ]  # get list of reprojected input files to merge
        out_name = f"{strip_scene_name(data=Path(files[0]))}_mosaic.tif"  # set output filename
        mosaic, transform = merge(img_list)  # merge rasters, return mosaic as array amd target transform

        with Image(data=mosaic, crs=img_list[0].crs, transform=transform) as mosaic_img:
            mosaic_img.write_to_file(
                path_to_file=self.data_dir.joinpath(out_name), dtype=mosaic.dtype, nodata=0, compress="lzw"
            )

            for item in img_list:
                item.close()  # close rasterio instances

        return self.data_dir.joinpath(out_name)

    def reproject_input(self, data: Path) -> Image:
        """Reproject input tiles to WGS84 as neighboring tiles may have different UTM projections."""
        img = Image(data=data)

        if img.dataset.res == (10, 10):  # refers to resolution of NIR dataset
            # warp to SWIR resolution
            img.warp(dst_crs=CRS({"init": "EPSG:4326"}), nodata=img.dataset.nodata, target_align=self.swir)

        else:
            img.warp(dst_crs=CRS({"init": "EPSG:4326"}), nodata=img.dataset.nodata)  # keep resolution

        return img

    def get_rasters(self: Event) -> None:
        """Open NIR and SWIR raster files."""
        self.swir = Image(data=self.get_swir_file())  # load swir first to have resolution reference
        self.nir = Image(data=self.get_nir_file())

    def crop_rasters(self: Event) -> None:
        """Crop NIR and SWIR rasters to the extent of the AOI."""
        self.nir.mask(bbox=self.aoi, crop=True)
        self.swir.mask(bbox=self.aoi, crop=True)

    def get_normalized_burnt_ratio(self: Event) -> None:
        """Get the normalized burnt ratio for this specific event."""
        self.get_rasters()
        self.crop_rasters()
        nbr = (self.nir.arr - self.swir.arr) / (self.nir.arr + self.swir.arr)  # compute NBR
        self.nbr = Image(
            data=nbr, crs=self.nir.dataset.crs, transform=self.nir.dataset.transform, nodata=self.nir.dataset.nodata
        )
        self.nbr.write_to_file(
            path_to_file=self.data_dir.joinpath(f"{self.event}_nbr.tif"), dtype=np.float32, nodata=0, compress="lzw"
        )


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
                nbr_pre, nbr_post = self.check_geometries(nbr_pre=pre_event.nbr, nbr_post=post_event.nbr)
                self.get_normalized_burnt_ratio_difference(nbr_pre=nbr_pre, nbr_post=nbr_post)

    @staticmethod
    def check_geometries(nbr_pre: Image, nbr_post: Image) -> tuple:
        """Check geometries of pre- and post-event NBR as the underlying datasets might be shifted."""
        if nbr_pre.arr.shape != nbr_post.arr.shape:
            nbr_pre.warp(dst_crs=nbr_post.dataset.crs, nodata=nbr_post.dataset.nodata, target_align=nbr_post)

        return nbr_pre, nbr_post

    def get_normalized_burnt_ratio_difference(self: BurntAreaMapper, nbr_pre: Image, nbr_post: Image) -> None:
        """Compute the difference of the pre-event NBR and the post-event NBR."""
        dnbr = nbr_pre.arr - nbr_post.arr
        self.dnbr = Image(
            data=dnbr, crs=nbr_pre.dataset.crs, transform=nbr_pre.dataset.transform, nodata=nbr_pre.dataset.nodata
        )
        self.dnbr.write_to_file(
            path_to_file=self.out_dir.joinpath("dnbr.tif"), dtype=np.float32, nodata=0, compress="lzw"
        )

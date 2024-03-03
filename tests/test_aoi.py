"""Test anomaly detection."""
from __future__ import annotations

import unittest
from pathlib import Path

from fiona import errors as ferrors
from fiona.collection import Collection
from shapely import errors
from shapely.geometry.polygon import Polygon

from demeter.aoi_check import AOI

TEST_DIR = Path.cwd()


class TestAOI(unittest.TestCase):
    """Encapsulates testing methods."""

    def __init__(self: TestAOI, *args: int, **kwargs: int) -> None:
        """Initialize TestAOI class."""
        super().__init__(*args, **kwargs)

    def test_open_aoi_file(self: TestAOI) -> None:
        """Test open AOI file."""
        # provide as pathlib.Path
        with AOI(data=TEST_DIR.joinpath("alpha_road_tambaroora.gpkg")) as aoi:
            self.assertTrue(isinstance(aoi.filename, Path))
            self.assertTrue(isinstance(aoi.aoi, Collection))

        # provide as string
        with AOI(data=str(TEST_DIR.joinpath("alpha_road_tambaroora.gpkg").absolute())) as aoi:
            self.assertTrue(isinstance(aoi.filename, Path))
            self.assertTrue(isinstance(aoi.aoi, Collection))

    def test_fail_open_aoi_file(self: TestAOI) -> None:
        """Test open missing AOI file."""
        # provide as pathlib.Path
        with self.assertRaises(ferrors.DriverError):
            aoi_collection = AOI(data=TEST_DIR.joinpath("MISSING.gpkg"))
            aoi_collection.close()

        with self.assertRaises(TypeError):
            aoi_collection = AOI(data=str(TEST_DIR.joinpath("MISSING.gpkg").absolute()))
            aoi_collection.close()

    def test_get_aoi_features(self: TestAOI) -> None:
        """Test AOI with features."""
        # provide as pathlib.Path
        with AOI(data=TEST_DIR.joinpath("alpha_road_tambaroora.gpkg")) as aoi:
            self.assertTrue(isinstance(aoi.features, list))

            if len(aoi.features) > 1:
                self.assertTrue(isinstance(aoi.geometry, tuple))

            else:  # only one feature given
                self.assertTrue(isinstance(aoi.geometry, tuple))

    def test_get_aoi_no_features(self: TestAOI) -> None:
        """Test empty AOI."""
        # provide as pathlib.Path
        with self.assertRaises(AttributeError):
            aoi_collection = AOI(data=TEST_DIR.joinpath("empty.gpkg"))
            aoi_collection.close()

    def test_aoi_from_file_string(self: TestAOI) -> None:
        """Test AOI from file string."""
        with AOI(data=str(TEST_DIR.joinpath("alpha_road_tambaroora.gpkg").absolute())) as aoi:
            self.assertTrue(isinstance(aoi.geometry, tuple))

    def test_aoi_from_polygon(self: TestAOI) -> None:
        """Test AOI from polygon."""
        pol = Polygon(((148, -33), (148, -32), (150, -32), (150, -33), (148, -33)))

        with AOI(data=pol) as aoi:
            self.assertTrue(isinstance(aoi.geometry, tuple))

    def test_aoi_from_wkt(self: TestAOI) -> None:
        """Test AOI from WKT."""
        pol = "POLYGON ((148 -33, 148 -32, 150 -32, 150 -33, 148 -33))"

        with AOI(data=pol) as aoi:
            self.assertTrue(isinstance(aoi.geometry, tuple))

    def test_aoi_from_wkt_errors(self: TestAOI) -> None:
        """Test AOI from errorness WKT string."""
        pol = "POLYGON((148, -33), (148, -32), (150, -32), (150, -33), (148, -33))"

        with self.assertRaises(errors.GEOSException):
            aoi = AOI(data=pol)
            aoi.close()

        pol = "polygon ((148 -33, 148 -32, 150 -32, 150 -33, 148 -33))"

        with self.assertRaises(TypeError):
            aoi = AOI(data=pol)
            aoi.close()

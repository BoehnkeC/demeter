from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np


def strip_scene_name(data: str | Path) -> str:
    """Remove tile ID from scene name, e.g. T56HKJ."""
    if isinstance(data, str):
        scene = data  # e.g. S2A_T56HKJ_20230305_0_L2A_B8A

    elif isinstance(data, Path):
        scene = Path(data).stem  # Path(S2A_20230305_0_L2A_pre/S2A_T56HKJ_20230305_0_L2A_B8A.tif)

    else:
        raise TypeError(f"The provided type for {data} is {type(data)}, which is not supported.")

    stripped_scene = scene.split("_")
    stripped_scene.pop(1)

    return "_".join(stripped_scene)


def alter_date(date: str, operator: str = "+", delta: int = 10) -> str:
    """Add or substract 10 days from start or end date."""
    if operator == "+":
        return datetime.strftime(datetime.strptime(date, "%Y-%m-%d") + timedelta(delta), "%Y-%m-%d")

    else:
        return datetime.strftime(datetime.strptime(date, "%Y-%m-%d") - timedelta(delta), "%Y-%m-%d")


def get_closest_date(date_list, date, start=True):
    """Find the closest date in relation to a given date."""
    date_list = [
        datetime.strptime(item.properties["created"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)
        for item in date_list
    ]
    date_list.sort()
    date = datetime.strptime(date, "%Y-%m-%d")

    if start:
        date = datetime.combine(date, datetime.min.time())
        return datetime.strftime(date_list[np.searchsorted(date_list, date, side="left") - 1], "%Y%m%d")

    else:
        date = datetime.combine(date, datetime.max.time())
        return datetime.strftime(date_list[np.searchsorted(date_list, date, side="right") + 1], "%Y%m%d")

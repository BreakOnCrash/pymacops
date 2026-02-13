from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import Quartz

from .screenshot import Screenshot
from .types import Point, Rect, Size
from pymacops import screenshot


@dataclass(frozen=True)
class DisplayInfo:
    display_id: int
    bounds: Rect
    pixel_size: Size


class DisplayManager:
    _curdisplay: Optional[DisplayInfo] = None
    _desktop_bounds: Optional[Rect] = None

    @property
    def curdisplay(self) -> DisplayInfo:
        # TODO, only support single display for now, need to support multiple displays in the future

        if not self._curdisplay:
            display_id = Quartz.CGMainDisplayID()
            _bounds = Quartz.CGDisplayBounds(display_id)
            self._curdisplay = DisplayInfo(display_id=display_id,
                                           bounds=Rect(
                                               float(_bounds.origin.x),
                                               float(_bounds.origin.y),
                                               float(_bounds.size.width),
                                               float(_bounds.size.height),
                                           ),
                                           pixel_size=Size(
                                               float(Quartz.CGDisplayPixelsWide(
                                                   display_id)),
                                               float(Quartz.CGDisplayPixelsHigh(
                                                   display_id)),
                                           ))

        return self._curdisplay

    def map_point(
        self,
        point: Point,
        screenshot: Screenshot,
        image_origin: str = "bottom-left",
    ) -> Point:
        if hasattr(screenshot, "cgimage"):
            cgimage = screenshot.cgimage
        else:
            cgimage = screenshot

        image_size = Size(
            float(Quartz.CGImageGetWidth(cgimage)),
            float(Quartz.CGImageGetHeight(cgimage)),
        )

        if image_origin == "bottom-left":
            point = Point(point.x, image_size.height - point.y)

        bounds = self.curdisplay.bounds
        point_in_points = Point(
            point.x * (bounds.width / image_size.width),
            point.y * (bounds.height / image_size.height),
        )
        return Point(
            bounds.x + point_in_points.x,
            bounds.y + (bounds.height - point_in_points.y),
        )

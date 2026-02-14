from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import Quartz
from PIL import Image

from .errors import PermissionDeniedError
from .types import Rect


@dataclass(frozen=True)
class Screenshot:
    cgimage: object

    def to_pil(self, convert_srgb: bool = True) -> Image.Image:
        width = Quartz.CGImageGetWidth(self.cgimage)
        height = Quartz.CGImageGetHeight(self.cgimage)

        if not convert_srgb:
            bytes_per_row = Quartz.CGImageGetBytesPerRow(self.cgimage)
            data_provider = Quartz.CGImageGetDataProvider(self.cgimage)
            data = Quartz.CGDataProviderCopyData(data_provider)
            buffer = bytes(data)
            return Image.frombuffer(
                "RGBA",
                (width, height),
                buffer,
                "raw",
                "RGBA",
                bytes_per_row,
                1,
            )

        color_space = Quartz.CGColorSpaceCreateWithName(
            Quartz.kCGColorSpaceSRGB
        )
        bytes_per_row = width * 4
        # macOS commonly uses BGRA in memory for 32-bit little-endian.
        bitmap_info = (
            Quartz.kCGImageAlphaPremultipliedFirst
            | Quartz.kCGBitmapByteOrder32Little
        )
        buffer = bytearray(bytes_per_row * height)
        context = Quartz.CGBitmapContextCreate(
            buffer,
            width,
            height,
            8,
            bytes_per_row,
            color_space,
            bitmap_info,
        )
        if not context:
            bytes_per_row = Quartz.CGImageGetBytesPerRow(self.cgimage)
            data_provider = Quartz.CGImageGetDataProvider(self.cgimage)
            data = Quartz.CGDataProviderCopyData(data_provider)
            raw_buffer = bytes(data)
            return Image.frombuffer(
                "RGBA",
                (width, height),
                raw_buffer,
                "raw",
                "RGBA",
                bytes_per_row,
                1,
            )
        Quartz.CGContextDrawImage(
            context,
            Quartz.CGRectMake(0, 0, width, height),
            self.cgimage,
        )
        return Image.frombuffer(
            "RGBA",
            (width, height),
            bytes(buffer),
            "raw",
            "BGRA",
            bytes_per_row,
            1,
        )


class Screenshotter:

    @staticmethod
    def capture(
        region: Optional[Rect] = None,
        window_id: Optional[int] = None,
        include_cursor: bool = False,
    ) -> Screenshot:
        if window_id is None:
            option = Quartz.kCGWindowListOptionOnScreenOnly
            target = Quartz.kCGNullWindowID
        else:
            option = Quartz.kCGWindowListOptionIncludingWindow
            target = window_id

        image = Quartz.CGWindowListCreateImage(
            Screenshotter._region_rect(region),
            option,
            target,
            Screenshotter._image_option(include_cursor),
        )
        if not image:
            raise PermissionDeniedError("Failed to capture screen image.")
        return Screenshot(image)

    @staticmethod
    def _region_rect(region: Optional[Rect]):
        if region is None:
            return Quartz.CGRectInfinite
        return Quartz.CGRectMake(region.x, region.y, region.width, region.height)

    @staticmethod
    def _image_option(include_cursor: bool):
        if include_cursor:
            return Quartz.kCGWindowImageDefault
        return Quartz.kCGWindowImageBoundsIgnoreFraming

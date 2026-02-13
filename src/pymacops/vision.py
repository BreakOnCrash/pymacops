from __future__ import annotations

from typing import Optional, List

import cv2
import numpy as np
from PIL import Image

import Quartz
from Vision import VNImageRequestHandler, VNRecognizeTextRequest

from .screenshot import Screenshot
from .types import Point, Rect, TextBlock


class ImageMatcher:

    def find_image(self, haystack: Image.Image, needle: Image.Image, threshold: float = 0.9) -> Optional[Point]:
        haystack_gray = cv2.cvtColor(np.array(haystack), cv2.COLOR_BGR2GRAY)
        needle_gray = cv2.cvtColor(np.array(needle), cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(
            haystack_gray, needle_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < threshold:
            return None

        return Point(float(max_loc[0]), float(max_loc[1]))


class BaseOCRReader:

    def read_text(
            self, image, languages) -> List[TextBlock]:
        raise NotImplementedError


class VisionOCR(BaseOCRReader):

    def read_text(
        self, image: Screenshot, languages: Optional[List[str]] = None
    ) -> List[TextBlock]:
        cgimage = self._to_cgimage(image)
        request = VNRecognizeTextRequest.alloc().init()
        if languages:
            request.setRecognitionLanguages_(languages)
        handler = VNImageRequestHandler.alloc().initWithCGImage_options_(
            cgimage, None
        )
        ok, _error = handler.performRequests_error_([request], None)
        if not ok:
            return []

        results = request.results() or []
        width = Quartz.CGImageGetWidth(cgimage)
        height = Quartz.CGImageGetHeight(cgimage)
        blocks: List[TextBlock] = []
        for observation in results:
            candidates = observation.topCandidates_(1)
            if not candidates:
                continue
            text = candidates[0].string()
            box = observation.boundingBox()
            bounds = Rect(
                float(box.origin.x * width),
                float((1.0 - box.origin.y - box.size.height) * height),
                float(box.size.width * width),
                float(box.size.height * height),
            )
            blocks.append(TextBlock(text=text, bounds=bounds))
        return blocks

    def find_text(
        self, image: Screenshot, 
        languages: Optional[List[str]] = None,
        text: str = None
    ) -> Optional[Point]:
        if not text:
            return None

        target = text.lower()
        blocks = self.read_text(image, languages=languages)
        for block in blocks:
            if block.bounds and target in block.text.lower():
                return Point(float(block.bounds.x), float(block.bounds.y))

        return None

    @staticmethod
    def _to_cgimage(image: Screenshot) -> Quartz.CGImageRef:
        if hasattr(image, "cgimage"):
            return image.cgimage
        return image

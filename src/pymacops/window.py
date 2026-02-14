from __future__ import annotations

from typing import Optional

import Quartz
from AppKit import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

from .types import Rect, WindowInfo


class WindowManager:

    @staticmethod
    def find_windows(text_contains: Optional[str] = None) -> list[WindowInfo]:
        windows = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
        )
        results: list[WindowInfo] = []
        for window in windows:
            title = window.get("kCGWindowName", "") or ""
            owner = window.get("kCGWindowOwnerName", "") or ""

            if text_contains and text_contains.lower() not in title.lower() and text_contains.lower() not in owner.lower():
                continue

            owner_pid = int(window.get("kCGWindowOwnerPID", 0))
            window_id = int(window.get("kCGWindowNumber", 0))
            bounds_dict = window.get("kCGWindowBounds", {}) or {}
            bounds = Rect(
                float(bounds_dict.get("X", 0.0)),
                float(bounds_dict.get("Y", 0.0)),
                float(bounds_dict.get("Width", 0.0)),
                float(bounds_dict.get("Height", 0.0)),
            )

            results.append(WindowInfo(
                window_id=window_id,
                title=title,
                owner_name=owner,
                owner_pid=owner_pid,
                bounds=bounds,
            ))

        return results

    @staticmethod
    def find_first(
        text_contains: Optional[str] = None,
    ) -> Optional[WindowInfo]:
        windows = WindowManager.find_windows(text_contains=text_contains)
        return windows[0] if windows else None

    @staticmethod
    def activate(window: WindowInfo) -> bool:
        app = NSRunningApplication.runningApplicationWithProcessIdentifier_(
            window.owner_pid
        )
        if not app:
            return False
        return bool(app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps))

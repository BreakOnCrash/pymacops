from __future__ import annotations

from typing import Optional

import Quartz
from AppKit import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

from .types import Rect, WindowInfo, first_or_none



class WindowManager:

    def list_windows(self) -> list[WindowInfo]:
        windows = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
        )
        results: list[WindowInfo] = []
        for window in windows:
            title = window.get("kCGWindowName", "") or ""
            owner = window.get("kCGWindowOwnerName", "") or ""
            owner_pid = int(window.get("kCGWindowOwnerPID", 0))
            window_id = int(window.get("kCGWindowNumber", 0))
            bounds_dict = window.get("kCGWindowBounds", {}) or {}
            bounds = Rect(
                float(bounds_dict.get("X", 0.0)),
                float(bounds_dict.get("Y", 0.0)),
                float(bounds_dict.get("Width", 0.0)),
                float(bounds_dict.get("Height", 0.0)),
            )
            results.append(
                WindowInfo(
                    window_id=window_id,
                    title=title,
                    owner_name=owner,
                    owner_pid=owner_pid,
                    bounds=bounds,
                )
            )
        return results

    def find_windows(
        self,
        text_contains: Optional[str] = None,
    ) -> list[WindowInfo]:
        windows = self.list_windows()
        return [
            w
            for w in windows
            if self._matches(w, text_contains)
        ]

    def find_first(
        self,
        text_contains: Optional[str] = None,
    ) -> Optional[WindowInfo]:
        return first_or_none(
            self.find_windows(
                text_contains=text_contains,
            )
        )

    def activate_app_for_window(self, window: WindowInfo) -> bool:
        app = NSRunningApplication.runningApplicationWithProcessIdentifier_(
            window.owner_pid
        )
        if not app:
            return False
        return bool(app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps))

    @staticmethod
    def _matches(
        window: WindowInfo,
        text_contains: Optional[str],
    ) -> bool:
        return text_contains and text_contains.lower() in window.title.lower() or \
            text_contains and text_contains.lower() in window.owner_name.lower()

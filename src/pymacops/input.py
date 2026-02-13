from __future__ import annotations

import time
from enum import IntEnum
from typing import Iterable, Optional

import Quartz

from .errors import PermissionDeniedError
from .types import Point


class MouseButton(IntEnum):
    LEFT = Quartz.kCGMouseButtonLeft
    RIGHT = Quartz.kCGMouseButtonRight
    CENTER = Quartz.kCGMouseButtonCenter


class KeyCode(IntEnum):
    ESCAPE = 53
    TAB = 48
    SPACE = 49
    ENTER = 36
    DELETE = 51
    LEFT = 123
    RIGHT = 124
    DOWN = 125
    UP = 126
    COMMAND = 55
    SHIFT = 56
    OPTION = 58
    CONTROL = 59


class Mouse:
    def __init__(self, default_delay: float = 0.01) -> None:
        self.default_delay = default_delay

    def move(self, point: Point) -> None:
        self._warp_mouse(point)

    def click(
        self,
        point: Point,
        button: MouseButton = MouseButton.LEFT,
        delay: Optional[float] = None,
    ) -> None:
        down_event, up_event = self._click_event_types(button)
        self._post_mouse_event(down_event, point, button)
        self._sleep(delay)
        self._post_mouse_event(up_event, point, button)

    def right_click(self, point: Point, delay: Optional[float] = None) -> None:
        self.click(point, button=MouseButton.RIGHT, delay=delay)

    def drag(self, start: Point, end: Point, delay: Optional[float] = None) -> None:
        self._post_mouse_event(
            Quartz.kCGEventLeftMouseDown, start, MouseButton.LEFT)
        self._sleep(delay)
        self._post_mouse_event(
            Quartz.kCGEventLeftMouseDragged, end, MouseButton.LEFT)
        self._sleep(delay)
        self._post_mouse_event(
            Quartz.kCGEventLeftMouseUp, end, MouseButton.LEFT)

    def scroll(self, delta_x: int, delta_y: int) -> None:
        event = Quartz.CGEventCreateScrollWheelEvent(
            None, Quartz.kCGScrollEventUnitLine, 2, delta_y, delta_x
        )
        if not event:
            raise PermissionDeniedError("Failed to create scroll event.")
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def _post_mouse_event(
        self, event_type: int, point: Point, button: MouseButton
    ) -> None:
        source = Quartz.CGEventSourceCreate(
            Quartz.kCGEventSourceStateHIDSystemState
        )
        if not source:
            raise PermissionDeniedError("Failed to create mouse event source.")
        event = Quartz.CGEventCreateMouseEvent(
            source,
            int(event_type),
            (float(point.x), float(point.y)),
            int(button),
        )
        if not event:
            raise PermissionDeniedError("Failed to create mouse event.")
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def _warp_mouse(self, point: Point) -> None:
        Quartz.CGAssociateMouseAndMouseCursorPosition(True)
        Quartz.CGWarpMouseCursorPosition((point.x, point.y))

    def _click_event_types(self, button: MouseButton) -> tuple[int, int]:
        if button == MouseButton.RIGHT:
            return (Quartz.kCGEventRightMouseDown, Quartz.kCGEventRightMouseUp)
        if button == MouseButton.CENTER:
            return (Quartz.kCGEventOtherMouseDown, Quartz.kCGEventOtherMouseUp)
        return (Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp)

    def _sleep(self, delay: Optional[float]) -> None:
        time.sleep(self.default_delay if delay is None else delay)


class Keyboard:
    """Keyboard input controller using Quartz."""

    def __init__(self, default_delay: float = 0.01) -> None:
        self.default_delay = default_delay

    def tap_key(self, keycode: KeyCode, delay: Optional[float] = None) -> None:
        self.key_down(keycode)
        self._sleep(delay)
        self.key_up(keycode)

    def key_down(self, keycode: KeyCode) -> None:
        event = Quartz.CGEventCreateKeyboardEvent(None, int(keycode), True)
        if not event:
            raise PermissionDeniedError("Failed to create key down event.")
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def key_up(self, keycode: KeyCode) -> None:
        event = Quartz.CGEventCreateKeyboardEvent(None, int(keycode), False)
        if not event:
            raise PermissionDeniedError("Failed to create key up event.")
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def type_text(self, text: str, delay: Optional[float] = None) -> None:
        for char in text:
            event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
            if not event:
                raise PermissionDeniedError("Failed to create text event.")
            Quartz.CGEventKeyboardSetUnicodeString(event, len(char), char)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
            self._sleep(delay)

    def chord(self, keys: Iterable[KeyCode], delay: Optional[float] = None) -> None:
        keys_list = list(keys)
        for key in keys_list:
            self.key_down(key)
        self._sleep(delay)
        for key in reversed(keys_list):
            self.key_up(key)

    def _sleep(self, delay: Optional[float]) -> None:
        time.sleep(self.default_delay if delay is None else delay)

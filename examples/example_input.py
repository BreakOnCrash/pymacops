from pymacops import Mouse, Screenshotter, WindowManager, DisplayManager, OpsVision


def main() -> None:
    window_text = "Chrome"
    target_text = "buzz"

    window = WindowManager.find_first(text_contains=window_text)
    if not window:
        print(f"No matching window found for: {window_text}")
        return
    WindowManager.activate(window)

    screenshot = Screenshotter.capture(window_id=window.window_id)
    point = OpsVision.find_text(screenshot, languages=[
                                "zh-Hans"], text=target_text)
    if not point:
        print(f"Text not found: {target_text}")
        return

    screen_point = DisplayManager.map_point(point, screenshot)
    print(
        f"Mapped point to screen coordinates: x={screen_point.x:.1f}, y={screen_point.y:.1f}")

    mouse = Mouse()
    mouse.click(screen_point)

    print(f"Moved mouse to x={screen_point.x:.1f}, y={screen_point.y:.1f}")


if __name__ == "__main__":
    main()

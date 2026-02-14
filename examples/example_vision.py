from pathlib import Path

from PIL import Image

from pymacops import Screenshotter, OpsVision, WindowManager


def find_image() -> None:
    # Capture full screen and load the needle image.
    haystack = Screenshotter.capture().to_pil()
    haystack.save(Path("screenshots") / "find_image.png")

    needle = Image.open(Path(__file__).parent / "example_find_image_1.png")

    match = OpsVision.find_image(haystack, needle)
    if match is None:
        print("No match found.")
        return

    print(f"Match at x={match.x:.1f}, y={match.y:.1f}")


def find_text() -> None:
    window = WindowManager.find_first(text_contains="Chrome")
    if not window:
        print("No matching window found.")
        return

    # Capture window, save a PIL copy, but pass CGImage-backed object to OCR.
    screenshot = Screenshotter.capture(window_id=window.window_id)
    image = screenshot.to_pil()
    image.save(Path("screenshots") / "find_text.png")

    point = OpsVision.find_text(screenshot, languages=["zh-Hans"], text="图片")
    if point:
        print(f"Found text at x={point.x:.1f}, y={point.y:.1f}")
    else:
        print("Text not found.")


if __name__ == "__main__":
    # find_image()
    find_text()

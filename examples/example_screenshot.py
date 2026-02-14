from pathlib import Path

from pymacops import Screenshotter, WindowManager


def main() -> None:
    window = WindowManager.find_first(owner_contains="Safari")
    if not window:
        print("No matching window found.")
        return

    shot = Screenshotter.capture(window_id=window.window_id)
    image = shot.to_pil()

    output_path = Path("screenshots") / "window.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"Saved window screenshot to {output_path}")

if __name__ == "__main__":
    main()

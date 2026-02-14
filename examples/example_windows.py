from pymacops import WindowManager


def main() -> None:
    print("All windows:")
    for window in WindowManager.find_windows():
        print(
            f"- {window.owner_name} | {window.title} | id={window.window_id} | "
            f"bounds={window.bounds.as_tuple()}"
        )

    print("\nFilter by title or owner contains 'Safari':")
    for window in WindowManager.find_windows(text_contains="Safari"):
        print(
            f"- {window.owner_name} | {window.title} | id={window.window_id}"
        )

    print("\nFind first window with title or owner contains 'Terminal':")
    window = WindowManager.find_first(text_contains="Terminal")
    if window:
        print(
            f"- {window.owner_name} | {window.title} | id={window.window_id}"
        )


if __name__ == "__main__":
    main()

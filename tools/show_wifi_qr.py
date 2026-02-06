import sys

from PIL import Image

try:
    from matrix_display import create_matrix, show_image
except ImportError:
    create_matrix = None
    show_image = None


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: show_wifi_qr.py <qr_image_path>")

    if create_matrix is None or show_image is None:
        print("show_wifi_qr: matrix_display not available; skipping display.")
        return

    image_path = sys.argv[1]
    image = Image.open(image_path).convert("RGB")

    matrix = create_matrix()
    show_image(matrix, image)


if __name__ == "__main__":
    main()

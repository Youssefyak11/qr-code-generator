import os
import sys
import argparse
import logging
from datetime import datetime

import qrcode
from qrcode.constants import ERROR_CORRECT_L

LOG_DIR = os.getenv("LOG_DIR", "./logs")
DEFAULT_OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./qr_codes")
DEFAULT_URL = os.getenv("URL", "https://github.com/kaw393939")

def setup_logging() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"),
        ],
    )

def validate_url(url: str) -> None:
    # Lightweight sanity check (keeps dependencies minimal)
    if not isinstance(url, str) or len(url.strip()) == 0:
        raise ValueError("URL cannot be empty.")
    lowered = url.lower()
    if not (lowered.startswith("http://") or lowered.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")

def build_qr(url: str, box_size: int, border: int, error_correction=ERROR_CORRECT_L):
    qr = qrcode.QRCode(
        version=None,  # let library choose best fit
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def save_qr(img, output_dir: str, filename: str | None = None) -> str:
    os.makedirs(output_dir, exist_ok=True)
    if not filename:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"qr_{ts}.png"
    path = os.path.join(output_dir, filename)
    img.save(path)
    return path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QR Code Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="The URL/text to encode into a QR code (can also set via env var URL).",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for generated QR files (env var OUTPUT_DIR).",
    )
    parser.add_argument(
        "--filename",
        default=None,
        help="Optional output filename (e.g., qr.png). If omitted, a timestamped name is used.",
    )
    parser.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="Pixel size of each QR box.",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="Border width (boxes).",
    )
    return parser.parse_args()

def main() -> int:
    setup_logging()
    args = parse_args()
    try:
        logging.info("Starting QR generation...")
        logging.info("Parameters: url=%s out=%s filename=%s box_size=%s border=%s",
                     args.url, args.out, args.filename, args.box_size, args.border)
        validate_url(args.url)
        img = build_qr(args.url, box_size=args.box_size, border=args.border)
        out_path = save_qr(img, args.out, args.filename)
        logging.info("QR Code saved to %s", out_path)
        print(f"QR Code saved to {out_path}")  # also print for `docker logs`
        return 0
    except Exception as e:
        logging.exception("Failed to generate QR code: %s", e)
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

from pathlib import Path
import re
import sys

from PIL import Image, ImageOps, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INCOMING_ROOT = PROJECT_ROOT / "incoming"
OUTPUT_ROOT = PROJECT_ROOT / "core" / "static" / "core" / "img" / "projects"
SUPPORTED_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def convert_image(source: Path, destination: Path) -> None:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        if image.width > 1600:
            resized_height = round(image.height * 1600 / image.width)
            image = image.resize((1600, resized_height), Image.Resampling.LANCZOS)

        has_alpha = "A" in image.getbands() or "transparency" in image.info
        image = image.convert("RGBA" if has_alpha else "RGB")
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="WEBP", quality=80, method=6)


def main() -> int:
    if not INCOMING_ROOT.is_dir():
        print(
            f"Input folder not found: {INCOMING_ROOT}\n"
            "Create incoming/<project-slug>/ and place image files there.",
            file=sys.stderr,
        )
        return 1

    converted = 0
    errors = 0
    project_dirs = sorted(path for path in INCOMING_ROOT.iterdir() if path.is_dir())
    if not project_dirs:
        print("No project folders found. Expected incoming/<project-slug>/<image>.")
        return 1

    for project_dir in project_dirs:
        slug = project_dir.name
        if not SLUG_PATTERN.fullmatch(slug):
            print(f"Invalid project folder slug: {slug!r} (use lowercase kebab-case).", file=sys.stderr)
            errors += 1
            continue

        sources = sorted(
            path
            for path in project_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        for source in sources:
            destination = OUTPUT_ROOT / slug / f"{source.stem}.webp"
            if destination.exists():
                print(f"Refusing to overwrite existing image: {destination}", file=sys.stderr)
                errors += 1
                continue
            try:
                convert_image(source, destination)
            except (OSError, UnidentifiedImageError, ValueError) as error:
                print(f"Could not convert {source}: {error}", file=sys.stderr)
                errors += 1
                continue

            static_path = Path("core") / "img" / "projects" / slug / destination.name
            print(f"{static_path.as_posix()}")
            converted += 1

    if converted == 0 and errors == 0:
        print("No supported image files found in the project folders.")
        return 1
    print(f"Converted {converted} image(s); {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

OUTPUT_DIR = Path(BASE_DIR / "output")
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir()

IDS_DIR = Path(BASE_DIR / "ids")

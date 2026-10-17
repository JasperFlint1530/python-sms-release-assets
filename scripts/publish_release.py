import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sms_template_service import InfraiClient, ReleaseNotice, publish_release_assets


def main() -> None:
    if not os.environ.get("INFRAI_API_KEY"):
        raise SystemExit("Set INFRAI_API_KEY before publishing release assets")
    notice = ReleaseNotice("ClipForge", "2026.09", "clipforge-release-2026-09", "clipforge")
    print(publish_release_assets(notice, InfraiClient()))


if __name__ == "__main__":
    main()

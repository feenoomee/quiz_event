"""Однократное сжатие уже загруженных изображений в media/uploads.

Конвертирует поддерживаемые изображения в WebP (качество 82), ограничивает
размер до 2000x2000, заменяет старый файл и обновляет ссылки в БД.

Запуск на сервере:
    ~/flaskenv/bin/python scripts/recompress_media.py
"""
import os
import sys
import uuid

from PIL import Image, ImageOps

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quiz_app import create_app, db  # noqa: E402
from quiz_app.models import User, Event, SitePoster  # noqa: E402

_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
_QUALITY = 82
_MAX_SIZE = (2000, 2000)


def recompress(src_path):
    img = Image.open(src_path)
    img.load()
    img = ImageOps.exif_transpose(img)
    img.thumbnail(_MAX_SIZE, Image.LANCZOS)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    out = os.path.join(os.path.dirname(src_path), f"{uuid.uuid4().hex}.webp")
    img.save(out, format="WEBP", quality=_QUALITY, method=6, optimize=True)
    return out


def main():
    app = create_app()
    uploads_root = os.path.join(app.root_path, "media", "uploads")
    if not os.path.isdir(uploads_root):
        print("No uploads folder:", uploads_root)
        return

    mapping = {}
    for sub in sorted(os.listdir(uploads_root)):
        subdir = os.path.join(uploads_root, sub)
        if not os.path.isdir(subdir):
            continue
        for fname in sorted(os.listdir(subdir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in _EXT:
                continue
            src = os.path.join(subdir, fname)
            try:
                if ext == ".webp":
                    with Image.open(src) as existing:
                        if existing.width <= _MAX_SIZE[0] and existing.height <= _MAX_SIZE[1]:
                            continue
                old_size = os.path.getsize(src)
                out = recompress(src)
                new_size = os.path.getsize(out)
                old_rel = f"uploads/{sub}/{fname}"
                new_rel = f"uploads/{sub}/{os.path.basename(out)}"
                os.remove(src)
                mapping[old_rel] = new_rel
                print(f"{old_size/1024:8.1f} KB -> {new_size/1024:8.1f} KB  {old_rel}")
            except Exception as e:
                print("SKIP", src, e)

    with app.app_context():
        updated = 0
        for u in User.query.filter(User.avatar.isnot(None)).all():
            if u.avatar in mapping:
                u.avatar = mapping[u.avatar]
                updated += 1
        for e in Event.query.all():
            if e.photo in mapping:
                e.photo = mapping[e.photo]
                updated += 1
            if e.result_photo in mapping:
                e.result_photo = mapping[e.result_photo]
                updated += 1
        for poster in SitePoster.query.all():
            if poster.photo in mapping:
                poster.photo = mapping[poster.photo]
                updated += 1
        db.session.commit()
        print(f"Updated {updated} DB references")


if __name__ == "__main__":
    main()

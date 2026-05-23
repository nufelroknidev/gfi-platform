from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB — anything larger is rejected outright
MAX_WIDTH = 1200  # px — images wider than this are scaled down


def process_image(image_field):
    """Validate size and resize an ImageField value in-place before save."""
    if not image_field:
        return

    if image_field.size > MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"Image file is too large ({image_field.size / 1024 / 1024:.1f} MB). "
            "Maximum allowed size is 10 MB."
        )

    img = Image.open(image_field)
    if img.width <= MAX_WIDTH:
        return

    ratio = MAX_WIDTH / img.width
    new_size = (MAX_WIDTH, int(img.height * ratio))
    img = img.resize(new_size, Image.LANCZOS)

    # Preserve format; fall back to JPEG for unknown formats
    fmt = img.format or "JPEG"
    if fmt == "JPEG":
        img = img.convert("RGB")  # strip alpha channel which JPEG cannot encode

    buf = BytesIO()
    save_kwargs = {"format": fmt}
    if fmt == "JPEG":
        save_kwargs["quality"] = 85
        save_kwargs["optimize"] = True

    img.save(buf, **save_kwargs)
    image_field.seek(0)
    image_field.file = ContentFile(buf.getvalue())
    image_field.file.seek(0)
    # Update the size attribute so Django stores the correct value
    image_field._size = buf.tell()

"""Shared file upload utilities for the public frontend."""
import os
import uuid

from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_DOC_EXTS = {'jpg', 'jpeg', 'png', 'pdf'}


def save_upload(file, subdirectory, prefix='file', allowed_exts=None):
    """Save an uploaded file and return its URL path.

    Args:
        file: FileStorage from request.files
        subdirectory: e.g. 'posts', 'campaigns', 'avatars'
        prefix: filename prefix, e.g. 'post', 'avatar'
        allowed_exts: set of allowed extensions (default: ALLOWED_IMAGE_EXTS)

    Returns:
        URL path string like '/static/upload/posts/post_abc123.jpg', or None if invalid.
    """
    if not file or not file.filename:
        return None

    if allowed_exts is None:
        allowed_exts = ALLOWED_IMAGE_EXTS

    filename = secure_filename(file.filename)
    if '.' not in filename:
        return None

    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_exts:
        return None

    safe_name = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"
    upload_dir = os.path.join('static', 'upload', subdirectory)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, safe_name)
    file.save(filepath)
    return '/' + filepath


def save_multiple_uploads(files, subdirectory, prefix='file', max_count=9, allowed_exts=None):
    """Save multiple uploaded files. Returns list of URL paths."""
    urls = []
    for f in files[:max_count]:
        url = save_upload(f, subdirectory, prefix, allowed_exts)
        if url:
            urls.append(url)
    return urls

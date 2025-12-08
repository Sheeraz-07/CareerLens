import os
from werkzeug.utils import secure_filename

ALLOWED_EXT = {"pdf", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def save_upload(fileobj, upload_folder):
    filename = secure_filename(fileobj.filename)
    path = os.path.join(upload_folder, filename)
    # handle duplicates e.g. add timestamp
    if os.path.exists(path):
        base, ext = os.path.splitext(filename)
        import time
        filename = f"{base}_{int(time.time())}{ext}"
        path = os.path.join(upload_folder, filename)
    fileobj.save(path)
    return filename, path

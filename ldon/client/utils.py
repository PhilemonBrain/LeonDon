import secrets
import os
from flask import current_app
from PIL import Image


def save_picture(form_picture):
    token_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = token_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics/' + picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

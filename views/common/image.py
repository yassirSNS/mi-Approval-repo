from flask import request
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
import time
from google.appengine.ext import blobstore
from google.appengine.api import images
# from PIL import Image
from views.common.cloud_storage import BUCKET, upload_object

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

USER_PROFILE = 1
CIRCLE_PROFILE = 2


def upload_image(entity_id, old_key, image_type):
    try:
        # check if the post request has the file part
        if 'photo' not in request.files:
            raise ValueError('No photo part')

        image_file = request.files['photo']

        # if user does not select file, browser also submit a empty part without filename
        if image_file and image_file.filename == '':
            raise ValueError('No file selected')

        ext = allowed_file(image_file.filename)

        # if allowed extension
        if ext:
            # img = Image.open(image_file)
            #
            # # Resize image
            # img.thumbnail((560, 560), Image.ANTIALIAS)
            #
            # # Convert Image to FileStorage type
            # sio = StringIO()
            # sio.name = image_file.filename
            # img.save(sio)
            # sio.seek(0)
            # f = FileStorage(sio)

            timestamp = int(time.mktime(datetime.utcnow().timetuple()))
            if image_type == USER_PROFILE:
                filename = 'user_profile/{}_{}.{}'.format(entity_id, timestamp, ext)
            elif image_type == CIRCLE_PROFILE:
                filename = 'circle_profile/{}_{}.{}'.format(entity_id, timestamp, ext)
            else:
                filename = '{}_{}.{}'.format(entity_id, timestamp, ext)

            res = upload_object(image_file, filename)

            # Delete old Serving URL and old Blob
            if old_key:
                images.delete_serving_url(old_key)
                blobstore.delete(old_key)

            # Create blob_key
            blob_key = blobstore.create_gs_key('/gs/{}/{}'.format(BUCKET, filename))

            return blob_key

        raise ValueError('Only .jpg, .jpeg, .png files are allowed')

    except RequestEntityTooLarge:
        raise ValueError('File is too large')


def delete_image(blob_key):
    if blob_key:
        images.delete_serving_url(blob_key)
        blobstore.delete(blob_key)


def allowed_file(filename):
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            return ext
    return False


# def resize_image(img):
#     base_width = 560
#     if img.size[0] > base_width:
#         w_percent = (base_width / float(img.size[0]))
#         h_size = int((float(img.size[1]) * float(w_percent)))
#         img = img.resize((base_width, h_size), Image.ANTIALIAS)
#     return img

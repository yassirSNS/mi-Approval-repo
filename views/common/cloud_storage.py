# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sample Google App Engine application that lists the objects in a Google Cloud
Storage bucket.

For more information about Cloud Storage, see README.md in /storage.
For more information about Google App Engine, see README.md in /appengine.
"""

import json
import io
import googleapiclient.discovery
import googleapiclient.http


# The bucket that will be used to list objects.
BUCKET = 'mi-approval-image'

storage = googleapiclient.discovery.build('storage', 'v1')


def upload_object(file_object, filename):
    body = {
        'name': filename
    }
    req = storage.objects().insert(
        bucket=BUCKET, body=body,
        media_body=googleapiclient.http.MediaIoBaseUpload(
            file_object, 'application/octet-stream'))
    resp = req.execute()
    return resp


def download_object(filename):
    # Use get_media instead of get to get the actual contents of the object.
    # http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#get_media
    req = storage.objects().get_media(bucket=BUCKET, object=filename)
    out_file = io.FileIO('sample.jpg', mode='wb')
    downloader = googleapiclient.http.MediaIoBaseDownload(out_file, req)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {}%.".format(int(status.progress() * 100)))

    return out_file


def delete_object(filename):
    req = storage.objects().delete(bucket=BUCKET, object=filename)
    resp = req.execute()
    return resp


def list_bucket_content():
    response = storage.objects().list(bucket=BUCKET).execute()
    return '<h3>Objects.list raw response:</h3>''<pre>{}</pre>'.format(
        json.dumps(response, sort_keys=True, indent=2))

import s3
import os
import io
from config import S3_KEY, S3_SECRET, S3_BUCKET, S3_LOCATION

test_filepath = './test/test_audio.wav'
s3_filepath = 'test/test_audio.wav'

def upload_bytes_test():
    with open(test_filepath, 'rb') as f:
        test_bytes = io.BytesIO(f.read())
        response = s3.upload_bytes_to_s3(test_bytes, s3_filepath)
        
        assert response == "{}{}".format(S3_LOCATION, s3_filepath)

def list_files_test():
    response = s3.list_objects_from_s3(prefix = 'test')

    assert s3_filepath in response



def delete_file_test():
    s3.delete_from_s3(s3_filepath)

upload_bytes_test()
list_files_test()
delete_file_test()

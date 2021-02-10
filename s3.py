import boto3
from config import S3_KEY, S3_SECRET, S3_BUCKET, S3_LOCATION

# application.config.from_object("config")
s3client = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)

# bucket_name = application.config["S3_BUCKET"]

def delete_from_s3(filename, bucket_name=S3_BUCKET):
	try:
		response = s3client.delete_object(
			Bucket = bucket_name,
			Key = filename
		)
		print("removed ", filename)
	except Exception as e:
		# This is a catch all exception, edit this part to fit your needs.
		print("Something Happened: ", e)
		return e
	return


def upload_bytes_to_s3(bytes, filename, bucket_name=S3_BUCKET, acl="public-read"):
	try:

		s3client.upload_fileobj(
			bytes,
			bucket_name,
			filename,
			# ExtraArgs={
			# 	"ACL": acl
			# }		
		)

	except Exception as e:
		# This is a catch all exception, edit this part to fit your needs.
		print("Something Happened: ", e)
		return e

	return "{}{}".format(S3_LOCATION, filename)

def upload_file_to_s3(fileToUpload, filepath, bucket_name=S3_BUCKET, acl="public-read"):
	try:

		s3client.upload_fileobj(
			fileToUpload,
			filepath,
			bucket_name,
			ExtraArgs={
				# "ACL": acl,
				"ContentType": fileToUpload.content_type
			}
		)

	except Exception as e:
		# This is a catch all exception, edit this part to fit your needs.
		print("Something Happened: ", e)
		return e

	return "{}{}".format(S3_LOCATION, filepath)

def list_objects_from_s3(prefix = '', bucket_name=S3_BUCKET):
    return [file["Key"] for file in s3client.list_objects(Bucket=bucket_name, Prefix = prefix)["Contents"]]
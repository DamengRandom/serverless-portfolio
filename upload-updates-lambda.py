import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes


def lambda_handler(event, context):
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    serverless_bucket = s3.Bucket("serverless.damengccp.com")
    build_bucket = s3.Bucket('serverlessbuild.damengccp.com')
    serverlessBuild_zip = StringIO.StringIO()
    build_bucket.download_fileobj('serverlessBuild.zip', serverlessBuild_zip)

    with zipfile.ZipFile(serverlessBuild_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            serverless_bucket.upload_fileobj(
                obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            serverless_bucket.Object(nm).Acl().put(ACL='public-read')

    return 'Hi there'

# How to run the code? In terminal pls type: /usr/local/bin/python2 upload-updates-lambda.py

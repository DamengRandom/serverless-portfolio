import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes


def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic(
        "arn:aws:sns:us-east-1:878359838010:deployServerlessTopic")
    location = {
        "bucketName": "serverlessbuild.damengccp.com",
        "objectKey": "serverlessBuild.zip"
    }
    try:
        job = event.get('CodePipeline.job')
        if job:
            for artifact in job['data']['inputArtifacts']:
                if artifact['name'] == 'BuildArtifact':
                    location = artifact['location']['s3Location']
        print "Building Serverless Portfolio from " + str(location)

        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        serverless_bucket = s3.Bucket("serverless.damengccp.com")
        build_bucket = s3.Bucket(location["bucketName"])
        serverlessBuild_zip = StringIO.StringIO()
        build_bucket.download_fileobj(
            location["objectKey"], serverlessBuild_zip)

        with zipfile.ZipFile(serverlessBuild_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                serverless_bucket.upload_fileobj(
                    obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                serverless_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Deployment Success",
                      Message="Hi there, serverless.damengccp.com has been deployed successfully.")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job['id'])
            print str(codepipeline)
    except:
        topic.publish(Subject="Deployment Failure",
                      Message="Oops, serverless.damengccp.com hasn't been deployed successfully..")

    return 'Hi there'

# How to run the code? In terminal pls type: /usr/local/bin/python2 upload-updates-lambda.py

#!/usr/bin/env python3

import os
import sys

sys.path.append("..") # to import higher level directories

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import boto3
from ctools.s3 import S3File
import zipfile

FILENAME = 'test-upload.zip'

if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--zipfile_up",required=True,help="name of zipfile to upload")
    parser.add_argument("--zipfile_dl",required=True,help="name of zipfile when downloaded.")
    args = parser.parse_args()

    assert os.path.exists(args.zipfile_up)


    # Boto3 Fileobject Zip testing
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('censyn.test')

    bucket.upload_file(args.zipfile_up, FILENAME)

    keys = {}

    for bucket_obj in bucket.objects.all():
        keys[bucket_obj.key] = bucket_obj.e_tag

    assert FILENAME in keys

    with open(args.zipfile_dl, 'wb') as f:
        bucket.download_fileobj(FILENAME, f)
        try:
            zf = zipfile.ZipFile(args.zipfile_dl, mode='r')
            print("Reading from file: Okay!")
        except zipfile.BadZipFile as e:
            print("Zip file could not be read: ", e)

        try:
            zf = zipfile.ZipFile(f, mode='r')
            print("Reading from file object: Okay!")
        except zipfile.BadZipFile as e:
            print("Zip file object could not be read: ", e)

    # S3File Testing
    s3zip = S3File('s3://censyn.test/' + FILENAME)
    zf = zipfile.ZipFile(s3zip, mode='r', allowZip64=True)
    print("Files in {}:".format(s3zip.name))
    file_list = []
    first = None
    for name in zf.namelist():
        print(name)
    print("\n")

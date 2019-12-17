3#!/usr/bin/env python3
# Test S3 code

import os
import pytest
import subprocess
import sys
import tempfile
import warnings

import boto3

sys.path.append( os.path.join( os.path.dirname(__file__), "../..") )

import ctools.s3 as s3

# NOTE: This will never find environment variables because of the way pytest generates tests.
## Find a S3 bucket for testing. This is either TEST_S3ROOT or DAS_S3ROOT
if "TEST_S3ROOT" in os.environ:
    TEST_S3ROOT = os.environ['TEST_S3ROOT']
elif "DAS_S3ROOT" in os.environ:
    TEST_S3ROOT = os.environ['DAS_S3ROOT']
else:
    TEST_S3ROOT = None

MOTD = 'etc/motd'
TEST_STRING  = "As it is written " + str(os.getpid()) + "\n"
TEST_S3_FILE = "Examples/testfile.txt"
TEST_S3BUCKET = "s3://censyn.test"

# Solution: https://stackoverflow.com/a/29854274
@pytest.fixture(scope='session', autouse=True)
def check_connection(timeout=5):
    """Checks for open connection to the internet"""
    import http
    conn = http.client.HTTPConnection("www.google.com", timeout=timeout)
    try:
        conn.request("HEAD", "/")
    except:
        warnings.warn("No connection to the internet detected")


@pytest.fixture(scope='function')
def create_temp_file():
    return tempfile.NamedTemporaryFile()

@pytest.fixture(scope='function')
def create_temp_dir():
    return tempfile.mkdtemp()

@pytest.fixture(scope='function')
def s3_tempfile_noremove():
    (bucket, key) = s3.get_bucket_key(TEST_S3BUCKET)
    s3bucket = boto3.resource('s3').Bucket(bucket)
    temp = tempfile.NamedTemporaryFile()
    return s3bucket.put_object(Body=temp.read(), Key=temp.name)


@pytest.fixture(scope='function')
def s3_tempfile_remove():
    (bucket, key) = s3.get_bucket_key(TEST_S3BUCKET)
    s3bucket = boto3.resource('s3').Bucket(bucket)
    temp = tempfile.NamedTemporaryFile()
    obj = s3bucket.put_object(Body=temp.read(), Key=temp.name)
    yield obj
    obj.delete()


def test_s3open(check_connection):

    if not check_connection:
        warnings.warn("test_s3open only runs when connected to the internet")
        return

    if "EC2_HOME" not in os.environ:
        warnings.warn("test_s3open only runs on AWS EC2 computers")
        return

    if TEST_S3ROOT is None:
        warnings.warn("no TEST_S3ROOT is defined.")
        return

    # Make sure attempt to read a file that doesn't exist gives a FileNotFound error
    got_exception = True
    try:
        f = s3.s3open("bad path")
        got_exception = False
    except ValueError as e:
        pass
    if got_exception==False:
        raise RuntimeError("should have gotten exception for bad path")

    # This is equivalent to the above
    # TODO: Cleanup above
    with pytest.raises(ValueError):
        f = s3.s3open("bad path")

    path = os.path.join( TEST_S3ROOT, TEST_S3_FILE)
    print("path:",path)

    # Make sure s3open works in a variety of approaches

    # Reading s3open as an iterator
    val1 = ""
    for line in s3.s3open(path,"r"):
        val1 += line 

    # Reading s3open with .read():
    f = s3.s3open(path,"r")
    val2 = f.read()

    # Reading s3open with a context manager
    with s3.s3open(path,"r") as f:
        val3 = f.read()

    assert val1==val2==val3


def test_s3open_write_fsync():
    """See if we s3open with the fsync option works"""
    if not check_connection:
        warnings.warn("test_s3open only runs when connected to the internet")
        return

    if "EC2_HOME" not in os.environ:
        warnings.warn("s3open only runs on AWS EC2 computers")
        return

    if TEST_S3ROOT is None:
        warnings.warn("no TEST_S3ROOT is defined.")
        return


    path = os.path.join( DAS_S3ROOT, f"tmp/tmp.{os.getpid()}")
    with s3.s3open(path,"w", fsync=True) as f:
        f.write( TEST_STRING)
    with s3.s3open(path,"r") as f:
        buf = f.read()
        print("Wanted: ",TEST_STRING)
        print("Got:: ",buf)
        assert buf==TEST_STRING

    try:
        s3.s3rm(path)
    except RuntimeError as e:
        print("path:",file=sys.stderr)
        raise e


def test_s3open_iter():
    if not check_connection:
        warnings.warn("test_s3open only runs when connected to the internet")
        return

    if "EC2_HOME" not in os.environ:
        warnings.warn("s3open only runs on AWS EC2 computers")
        return


    if TEST_S3ROOT is None:
        warnings.warn("no TEST_S3ROOT is defined.")
        return



    path = os.path.join(DAS_S3ROOT, f"tmp/tmp.{os.getpid()}")
    with s3.s3open(path,"w", fsync=True) as f:
        for i in range(10):
            f.write( TEST_STRING[:-1] + str(i) + "\n")

    with s3.s3open(path, "r") as f:
        fl = [l for l in f]
        for i, l in enumerate(fl):
            assert l == TEST_STRING[:-1]  + str(i) + "\n"

    f = s3.s3open(path, "r")
    fl = [l for l in f]
    for i, l in enumerate(fl):
        assert l == TEST_STRING[:-1] + str(i) + "\n"

    s3.s3rm(path)


def test_get_bucket_key():
    INVALID_S3_LOCATION = ""
    assert s3.get_bucket_key("s3://") == ('', '')
    with pytest.raises(ValueError) as e:
        s3.get_bucket_key(INVALID_S3_LOCATION)
        assert e.type() == ValueError
    
    assert s3.get_bucket_key("s3://test") == ('test','')
    assert s3.get_bucket_key("test/key") == ('test','key')
    assert s3.get_bucket_key("s3://test/key") == ('test','key')



def test_get_aws():
    aws = s3.get_aws()
    assert aws in s3.AWS_LIST
    assert os.path.exists(aws)

def test_aws_s3api():
    with pytest.raises(TypeError):
        s3.aws_s3api()
    # NOTE: Nothing to assert, so not sure what to test for here? That it runs?
    with pytest.raises(RuntimeError):
        s3.aws_s3api([])
    

# TODO: Figure out how to test this
def test_put_object(create_temp_file):
    (bucket, key) = s3.get_bucket_key(TEST_S3BUCKET)
    s3bucket = boto3.resource('s3').Bucket(bucket)
    s3.put_object(bucket, "TEMP_KEY",create_temp_file.name)
    objs = list(s3bucket.objects.filter(Prefix="TEMP_KEY"))
    assert len(objs) == 1
    # Cleanup
    s3bucket.delete_objects(Delete={
        "Objects":
        [{"Key": "TEMP_KEY"}]
        })

# TODO: Figure out how to test this
def test_put_s3url(create_temp_file):
    with pytest.raises(TypeError) as excinfo:
        s3.put_s3url(None, None)
        assert excinfo.type() == TypeError
    with pytest.raises(TypeError) as excinfo:
        s3.put_s3url(None, create_temp_file)
        assert excinfo.type() == TypeError
    
    s3.put_s3url(TEST_S3BUCKET + '/'.join(create_temp_file.name.split('/')[:-1]), create_temp_file.name)

    


# TODO: Figure out how to test this
def test_head_object(s3_tempfile_remove):
    (bucket, key) = s3.get_bucket_key(TEST_S3BUCKET)
    key = s3_tempfile_remove.key
    TEST_HEAD = boto3.client('s3').head_object(Bucket=bucket, Key=key)
    RES_HEAD = s3.head_object(bucket, key)
    del TEST_HEAD['ResponseMetadata']
    del RES_HEAD['ResponseMetadata']
    assert RES_HEAD == TEST_HEAD


# TODO: Figure out how to test this
def test_delete_object(s3_tempfile_noremove):
    (bucket, key) = s3.get_bucket_key(TEST_S3BUCKET)
    s3bucket = boto3.resource('s3').Bucket(bucket)
    test_obj = s3_tempfile_noremove
    remove_key = test_obj.key
    s3.delete_object(bucket, remove_key)
    objs = list(s3bucket.objects.filter(Prefix=remove_key))
    assert len(objs) == 0


def test_list_objects():
    s3.list_objects(TEST_S3BUCKET)


def test_mt_list_objects():
    # s3.mt_list_objects(TEST_S3BUCKET)
    pass

def test_sum_object_sizes():
    assert s3.sum_object_sizes([{'Size': 1}, {'Size': 1}]) == 2


def test_any_object_too_small():
    true_test = [{'Size': -1}]
    false_test = [{'Size': 1}]
    assert s3.any_object_too_small(true_test)
    assert not s3.any_object_too_small(false_test)


# TODO: Figure out how to test this
def test_download_object(create_temp_dir, s3_tempfile_remove):
    (bucket, key) = s3.get_bucket_key(TEST_S3BUCKET)
    s3.download_object(create_temp_dir, bucket, {'fname': s3_tempfile_remove.key, 'Key': s3_tempfile_remove.key})
    assert os.path.exists( os.path.join(create_temp_dir, s3_tempfile_remove.key) )


def test_concat_downloaded_objects():
    tf1 = tempfile.NamedTemporaryFile()
    tf2 = tempfile.NamedTemporaryFile()

    tf1.write(b"TEMP FILE 1")
    tf2.write(b"TEMP FILE TWO")
    tf1.seek(0)
    tf2.seek(0)

    tf1store = tf1.read()
    tf2store = tf2.read()


    obj1 = {'fname': tf1.name, 'Size': os.path.getsize(tf1.name)}
    obj2 = {'fname': tf2.name, 'Size': os.path.getsize(tf2.name)}

    tmp = ''
    with open(obj1['fname'], 'rb') as reader:
        tmp = reader.read()
        print(tmp)

    assert tmp == tf1store
    
    print(obj1, obj2)
    print(tf1store, tf2store)

    s3.concat_downloaded_objects(obj1, obj2)

    with open(obj1['fname'], 'rb') as reader:
        concat = reader.read()
    print(concat)

    concat_compare = tf1store + tf2store
    assert concat == concat_compare

def test_s3exists(s3_tempfile_remove):
    assert s3.s3exists("FILE DOES NOT EXIST") == False
    assert s3.s3exists(TEST_S3BUCKET + '/' + s3_tempfile_remove.key) == True


# TODO: Figure out how to test this
def test_s3rm():
    # Put S3 object in bucket
    # Make sure S3 object is in bucket
    # Remove S3 object
    # Check to see if S3 object was removed
    pass
    
if __name__=="__main__":
    test_s3open()
    test_s3open_write_fsync()

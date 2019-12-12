3#!/usr/bin/env python3
# Test S3 code

import os
import pytest
import subprocess
import sys
import tempfile
import warnings

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
def s3_tempfile():
    temp = tempfile.NamedTemporaryFile()
    # Maybe write out random junk to the file?
    return temp


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
    with pytest.raises(ValueError):
        s3.get_bucket_key(INVALID_S3_LOCATION)


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
def test_put_object():
    # Should raise a type error when when path is None
    with pytest.raises(TypeError):
        s3.put_object(TEST_S3ROOT, None, None)

    tf = tempfile.NamedTemporaryFile()
    print(TEST_S3ROOT, tf.name.split('/')[-1], tf.name)
    s3.put_object(TEST_S3ROOT, tf.name.split('/')[-1], tf.name)


    

# TODO: Figure out how to test this
def test_put_s3url(s3_tempfile):
    with pytest.raises(TypeError) as excinfo:
        s3.put_s3url(None, None)
        assert excinfo.type() == TypeError
    with pytest.raises(TypeError) as excinfo:
        s3.put_s3url(None, s3_tempfile)
        assert excinfo.type() == TypeError
    
    s3.put_s3url(TEST_S3BUCKET + '/'.join(s3_tempfile.name.split('/')[:-1]), s3_tempfile.name)

    


# TODO: Figure out how to test this
def test_head_object():
    with pytest.raises(RuntimeError) as excinfo:
        s3.head_object(None, None)
        assert excinfo.type() == RuntimeError

    # NOTE: Not sure what this is even supposed to return
    # but will figure out later
    s3.head_object(TEST_S3BUCKET, "HEAD_KEY")


# TODO: Figure out how to test this
def test_delete_object():
    # Make sure there's an object to delete
    # Try to delete that object
    # Check that the object was deleted
    pass


# TODO: Figure out how to test this
def test_list_objects():
    # Test list_objects when no objects are in the s3 bucket
    # Test list_objects when there are objects in the s3 bucket
    pass

# TODO: Figure out how to test this
def test_search_objects():
    # Test search_objects with there no are objects in the s3 bucket
    # Test search_objects with there are objects in the s3 bucket
    pass


def test_sum_object_sizes():
    assert s3.sum_object_sizes([{'Size': 1}, {'Size': 1}]) == 2


def test_any_object_too_small():
    true_test = [{'Size': -1}]
    false_test = [{'Size': 1}]
    assert s3.any_object_too_small(true_test)
    assert not s3.any_object_too_small(false_test)


# TODO: Figure out how to test this
def test_download_object():
    pass


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

# TODO: Figure out how to test this
# NOTE: There's a comment stating that this function needs to be replaced with an s3api function, so not gonna worry about this function yet.
def test_s3exists():
    assert s3.s3exists("THIS FILE DOES NOT EXIST") == False
    assert s3.s3exists("THIS FILE SHOULD EXIST") == True


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

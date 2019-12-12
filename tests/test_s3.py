#!/usr/bin/env python3
# Test S3 code
# (Might later be integrated into s3_test.py)

# Notes:
# 12/10/19
# My Main issue at the moment is trying to figure out 
# how exactly to consistently mock these functions. 
# Most of the functions that Simson wants me to test 
# for are just wrapper functions which should all work
# given that the aws-cli also works

import pytest
import subprocess
import tempfile
from ctools.s3 import *



def test_get_bucket_key(monkeypatch):
    INVALID_S3_LOCATION = ""

    assert get_bucket_key("s3://") == ('', '')
    # monkeypatch.setattr()
    with pytest.raises(ValueError):
        get_bucket_key(INVALID_S3_LOCATION)

def test_get_aws(monkeypatch):
    def mockexists(self):
        return True
    def mocknotexists(self):
        return False
    monkeypatch.setattr(os.path, "exists", mocknotexists)

    with pytest.raises(RuntimeError):
        get_aws()

    monkeypatch.setattr(os.path, "exists", mockexists)
    assert get_aws() in AWS_LIST # Is this necessary?


def test_aws_s3api():
    # monkeypatch get_aws() and test whether aws_s3api runs correctly
    pass
    

# TODO: Figure out how to test this
def test_put_object():
    # Assertion within the function when path does not exist
    with pytest.raises(TypeError):
        put_object(None, None, None)

    # Needs more cases

    

# TODO: Figure out how to test this
def test_put_s3url():
    pass


# TODO: Figure out how to test this
def test_head_object():
    pass


# TODO: Figure out how to test this
def test_delete_object():
    pass


# TODO: Figure out how to test this
def test_list_objects():
    # Test list_objects when no objects are in the s3 bucket

    # Test list_objects when there are objects in the s3 bucket


# TODO: Figure out how to test this
def test_search_objects():
    pass


# TODO: Figure out how to test this
# NOTE: Is it necessary to test this?
def test_sum_object_sizes():
    assert sum_object_sizes([{'Size': 1}, {'Size': 1}]) == 2


def test_any_object_too_small():
    true_test = [{'Size': -1}]
    false_test = [{'Size': 1}]
    assert any_object_too_small(true_test)
    assert not any_object_too_small(false_test)


# TODO: Figure out how to test this
def test_download_object():
    pass


# TODO: Figure out how to test this
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

    print(obj1, obj2)
    print(tf1store, tf2store)

    concat_downloaded_objects(obj1, obj2)

    concat = tf1.read()

    assert concat == tf1store + tf2store

# TODO: Figure out how to test this
# NOTE: There's a comment stating that this function needs to be replaced with an s3api function, so not gonna worry about this function yet.
def test_s3exists():
    pass


# TODO: Figure out how to test this
def test_s3rm():
    pass
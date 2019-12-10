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
def test_list_objects(monkeypatch):
    pass


# TODO: Figure out how to test this
def test_search_objects():
    pass


# TODO: Figure out how to test this
def test_etag():
    verify1 = {'ETag': 'VERIFICATION'}
    verify2 = {'ETag': '"VERIFICATION"'}
    # verify3 = {'ETag': '"VERIFICATION'}
    assert etag(verify1) == 'VERIFICATION'
    assert etag(verify2) == 'VERIFICATION'

    # This last one will fail because there is a " in the front, but not the back
    # assert etag(verify3) == 'VERIFICATION'


# TODO: Figure out how to test this
def test_object_sizes():
    verify_list = [{'Size': 0},{'Size': 1},{'Size': 2}]
    assert object_sizes(verify_list) == [0, 1, 2]


# TODO: Figure out how to test this
# NOTE: Is it necessary to test this?
def test_sum_object_sizes():
    pass


# TODO: Figure out how to test this
def test_any_object_too_small():
    pass


# TODO: Figure out how to test this
def test_download_object():
    pass


# TODO: Figure out how to test this
def test_concat_downloaded_objects():
    pass


# TODO: Figure out how to test this
def test_s3exists():
    pass


# TODO: Figure out how to test this
def test_s3rm():
    pass
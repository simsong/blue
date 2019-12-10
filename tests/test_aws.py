#!/usr/bin/env python3
# Test aws code

import pytest
from ctools.aws import *
import urllib.request
import http
import json


# Not sure if needed
# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     """Remove requests.sessions.Session.request for all tests."""
#     monkeypatch.delattr("requests.sessions.Session.request")

TEST_URL = "http://google.com"

class MockProxy:
    def __enter__():
        return self

    def __exit__():
        return

def test_proxy_on(monkeypatch):
    
    monkeypatch.setenv(BCC_HTTP_PROXY, "TEST_HTTP")
    monkeypatch.setenv(BCC_HTTPS_PROXY, "TEST_HTTPS")
    proxy_on()
    assert os.environ[HTTP_PROXY] == os.environ[BCC_HTTP_PROXY]
    assert os.environ[HTTPS_PROXY] == os.environ[BCC_HTTPS_PROXY]


def test_proxy_off():
    with pytest.raises(KeyError):
        proxy_off()
        assert os.environ[HTTP_PROXY]
        assert os.environ[HTTPS_PROXY]


# Tests if the Proxy class can be used as a context manager.
def test_Proxy_class():
    with Proxy() as p:
        pass

# NOTE: The urllib.urlopen function has been deprecated since Python 3.6
# LINK: https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen
def test_get_url(monkeypatch):
    TEST_RESPONSE = "TEST RESPONSE"

    def mockresponse(self):
        return TEST_RESPONSE.encode()
    monkeypatch.setattr(http.client.HTTPResponse, "read", mockresponse)
    # TODO: Need to figure out a way to not query google and still get this to work
    # Test will fail because a fake URL won't work, so I have to use a real URL
    assert get_url(TEST_URL) == TEST_RESPONSE

# NOTE: Might be dependent deprecated function
def test_get_url_json(monkeypatch):

    def mockresponse(self):
        return '{"mock_key": "mock_value"}'.encode()
    monkeypatch.setattr(http.client.HTTPResponse, "read", mockresponse)
    assert get_url_json(TEST_URL) == {"mock_key": "mock_value"}


# NOTE: Might be dependent deprecated function
def test_user_data():
    pass

# NOTE: Might be dependent deprecated function
def test_ami_id():
    pass

# NOTE: Might be dependent deprecated function
def test_instanceId():
    pass
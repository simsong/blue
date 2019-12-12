#!/usr/bin/env python3
# Test aws code

import os
import pytest
import ctools.aws as aws
import urllib.request
import http
import json


# Not sure if needed
# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     """Remove requests.sessions.Session.request for all tests."""
#     monkeypatch.delattr("requests.sessions.Session.request")

TEST_URL = "http://google.com"

@pytest.fixture(scope='session', autouse=True)
def set_env_variables():
    os.environ[aws.BCC_HTTP_PROXY] = 'X'
    os.environ[aws.BCC_HTTPS_PROXY] = 'X'


def test_proxy_on(monkeypatch):
    
    monkeypatch.setenv(aws.BCC_HTTP_PROXY, "TEST_HTTP")
    monkeypatch.setenv(aws.BCC_HTTPS_PROXY, "TEST_HTTPS")
    aws.proxy_on()
    assert os.environ[aws.HTTP_PROXY] == os.environ[aws.BCC_HTTP_PROXY]
    assert os.environ[aws.HTTPS_PROXY] == os.environ[aws.BCC_HTTPS_PROXY]


def test_proxy_off():
    with pytest.raises(KeyError):
        aws.proxy_off()
        assert os.environ[aws.HTTP_PROXY]
        assert os.environ[aws.HTTPS_PROXY]


# Tests if the Proxy class can be used as a context manager.
def test_Proxy_class(set_env_variables):
    # monkeypatch.setenv(aws.BCC_HTTP_PROXY, "TEST_HTTP")
    # monkeypatch.setenv(aws.BCC_HTTPS_PROXY, "TEST_HTTPS")
    with aws.Proxy() as p:
        assert aws.HTTP_PROXY in os.environ
        assert aws.HTTPS_PROXY in os.environ
        assert os.environ[aws.HTTP_PROXY]
        assert os.environ[aws.HTTPS_PROXY]


def test_get_url():
    # NOTE: The urllib.urlopen function has been deprecated since Python 3.6
    # LINK: https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen
    TEST_RESPONSE = "TEST RESPONSE"
    # TODO: Need to figure out a way to not query google and still get this to work
    # Test will fail because a fake URL won't work, so I have to use a real URL
    assert aws.get_url(TEST_URL) == TEST_RESPONSE

# NOTE: Might be dependent deprecated function
def test_get_url_json(monkeypatch):
    # TODO: Need to redo this
    assert aws.get_url_json(TEST_URL) == {"mock_key": "mock_value"}


# NOTE: Might be dependent deprecated function
# NOTE: ONLY ABLE TO BE RUN IN AWS EC2 SERVER
# NOTE: Dependent on hardcoded IP address
def test_user_data():
    pass

# NOTE: Might be dependent deprecated function
# NOTE: ONLY ABLE TO BE RUN IN AWS EC2 SERVER
# NOTE: Dependent on hardcoded IP address
def test_ami_id():
    pass

# NOTE: Might be dependent deprecated function
# NOTE: ONLY ABLE TO BE RUN IN AWS EC2 SERVER
# NOTE: Dependent on hardcoded IP address
def test_instanceId():
    pass


# NOTE: Might be dependent deprecated function
# NOTE: ONLY ABLE TO BE RUN IN AWS EC2 SERVER
# NOTE: Dependent on hardcoded IP address
def test_get_ipaddr():
    pass



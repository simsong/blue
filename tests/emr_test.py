#!/usr/bin/env python3
# Test EMR code
# (Might later be integrated into s3_test.py)


import pytest
import json
import ctools.emr as emr


# NOTE: Should this function be tested?
# Not sure since it essentially is just checking if the aws commandline is installed on the machine
def test_show_credentials():
    emr.show_credentials()


def test_decode_user_data():
    with pytest.raises(Exception) as excinfo:
        emr.decode_user_data("BAD DATA")
        assert excinfo.type() == json.decoder.JSONDecodeError

    # with pytest.raises


def test_user_data():
    # NOTE: NEED MOCKING BADLY
    with pytest.raises(FileNotFoundError):
        assert emr.user_data().contains("error")
        pass


# NOTE: What is run_command_on_host() ?
# NOTE: Should this be a test?
def test_get_instance_type():
    pass


def test_aws_emr_cmd():
    emr.aws_emr_cmd(["BAD_COMMAND"])


def test_list_clusters():
    clusters = emr.list_clusters()


def test_describe_cluster():
    cluster_info = emr.describe_cluster('0')
    cluster_info = emr.describe_cluster('-1')

def test_list_instances():
    instance_list = emr.list_instances()


def test_add_cluster_info():
    emr.add_cluster_info(None)


def test_complete_cluster_info():
    cci = emr.complete_cluster_info()
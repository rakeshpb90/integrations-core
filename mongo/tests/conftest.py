# (C) Datadog, Inc. 2010-2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import subprocess
import time
import os
import sys

import pytest

from datadog_checks.mongo import MongoDb

from . import common

@pytest.fixture
def aggregator():
    from datadog_checks.stubs import aggregator
    aggregator.reset()
    return aggregator

@pytest.fixture
def check():
    check = MongoDb('mongo', {}, {})
    return check

@pytest.fixture(scope="session")
def spin_up_mongo():
    """
    Start a cluster with one master, one replica and one unhealthy replica and
    stop it after the tests are done.
    If there's any problem executing docker-compose, let the exception bubble
    up.
    """
    env = os.environ

    args = [
        "docker-compose",
        "-f", os.path.join(common.HERE, 'compose', 'docker-compose.yml')
    ]

    subprocess.check_call(args + ["up", "-d"], env=env)

    compose_dir = os.path.join(common.HERE, 'compose')

    script_path = os.path.join(common.HERE, 'compose', 'init.sh')

    curdir = os.getcwd()
    os.chdir(compose_dir)
    subprocess.check_call(script_path, env=env)
    os.chdir(curdir)

    yield
    subprocess.check_call(args + ["down"], env=env)

# (C) Datadog, Inc. 2010-2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import subprocess
import time
import os
import sys
import logging

import pytest

from datadog_checks.mongo import MongoDb

from . import common

log = logging.getLogger('test_mongo')


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

    try:
        subprocess.check_call(args + ["up", "-d"], env=env)
        compose_dir = os.path.join(common.HERE, 'compose')
        script_path = os.path.join(common.HERE, 'compose', 'init.sh')
        curdir = os.getcwd()
        log.info(compose_dir)
        os.chdir(compose_dir)
        log.info(os.getcwd())
        subprocess.check_call(['docker-compose exec config01 sh -c "mongo --port 27017 < /scripts/init-configserver.js"'])
        subprocess.check_call(['docker-compose', 'exec', 'config01', 'sh', '-c', "'mongo --port 27017 < /scripts/init-configserver.js'"])
        subprocess.check_call(['docker-compose', 'exec', 'shard01a', 'sh', '-c', "'mongo --port 27018 < /scripts/init-shard01.js'"])
        subprocess.check_call(['docker-compose', 'exec', 'shard02a', 'sh', '-c', "'mongo --port 27019 < /scripts/init-shard02.js'"])
        subprocess.check_call(['docker-compose', 'exec', 'shard03a', 'sh', '-c', "'mongo --port 27020 < /scripts/init-shard03.js'"])
        subprocess.check_call(['docker-compose', 'exec', 'router', 'sh', '-c', "'mongo < /scripts/init-router.js'"])
        # subprocess.check_call([script_path], env=env)
        os.chdir(curdir)
    except Exception:
        subprocess.check_call(args + ["down"], env=env)
        try:
            subprocess.check_call(['docker', 'system', 'prune', '-af'])
        except:
            pass
        try:
            subprocess.check_call(['docker', 'volume', 'prune', '-f'])
        except:
            pass
        raise

    yield
    subprocess.check_call(args + ["down"], env=env)

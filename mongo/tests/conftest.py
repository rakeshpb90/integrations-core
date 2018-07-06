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

# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import pytest

from datadog_checks.openldap import OpenLDAP

pytestmark = pytest.mark.integration


def test_check(aggregator, check):
    aggregator.assert_all_metrics_covered()

# (C) Datadog, Inc. 2010-2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
from os import environ
import logging
import copy
import subprocess

import mock
import pytest
from datadog_checks.mongo import MongoDb

from . import common
import mock


@pytest.mark.unit
def test_build_metric_list(check):
    """
    Build the metric list according to the user configuration.
    Print a warning when an option has no match.
    """
    # Initialize check
    setattr(check, "log", mock.Mock())

    build_metric_list = check._build_metric_list_to_collect

    # Default metric list
    DEFAULT_METRICS = {
        m_name: m_type for d in [
            check.BASE_METRICS, check.DURABILITY_METRICS,
            check.LOCKS_METRICS, check.WIREDTIGER_METRICS,]
        for m_name, m_type in d.iteritems()
    }

    # No option
    no_additional_metrics = build_metric_list([])
    assert len(no_additional_metrics) == len(DEFAULT_METRICS)

    # Deprecate option, i.e. collected by default
    default_metrics = build_metric_list(['wiredtiger'])

    assert len(default_metrics) == len(DEFAULT_METRICS)
    assert check.log.warning.call_count == 1

    # One correct option
    default_and_tcmalloc_metrics = build_metric_list(['tcmalloc'])
    assert default_and_tcmalloc_metrics == len(DEFAULT_METRICS) + len(check.TCMALLOC_METRICS)

    # One wrong and correct option
    default_and_tcmalloc_metrics = build_metric_list(['foobar', 'top'])
    assert len(default_and_tcmalloc_metrics) == len(DEFAULT_METRICS) + len(check.TOP_METRICS)
    assert self.check.log.warning.call_count == 2

# def test_metric_resolution(self):
#     """
#     Resolve metric names and types.
#     """
#     # Initialize check and tests
#     config = {
#         'instances': [self.MONGODB_CONFIG]
#     }
#     metrics_to_collect = {
#         'foobar': (GAUGE, 'barfoo'),
#         'foo.bar': (RATE, 'bar.foo'),
#         'fOoBaR': GAUGE,
#         'fOo.baR': RATE,
#     }
#     self.load_check(config)
#     resolve_metric = self.check._resolve_metric
#
#     # Assert
#
#     # Priority to aliases when defined
#     self.assertEquals((GAUGE, 'mongodb.barfoo'), resolve_metric('foobar', metrics_to_collect))
#     self.assertEquals((RATE, 'mongodb.bar.foops'), resolve_metric('foo.bar', metrics_to_collect))  # noqa
#     self.assertEquals((GAUGE, 'mongodb.qux.barfoo'), resolve_metric('foobar', metrics_to_collect, prefix="qux"))  # noqa
#
#     #  Resolve an alias when not defined
#     self.assertEquals((GAUGE, 'mongodb.foobar'), resolve_metric('fOoBaR', metrics_to_collect))
#     self.assertEquals((RATE, 'mongodb.foo.barps'), resolve_metric('fOo.baR', metrics_to_collect))  # noqa
#     self.assertEquals((GAUGE, 'mongodb.qux.foobar'), resolve_metric('fOoBaR', metrics_to_collect, prefix="qux"))  # noqa
#
# def test_metric_normalization(self):
#     """
#     Metric names suffixed with `.R`, `.r`, `.W`, `.w` are renamed.
#     """
#     # Initialize check and tests
#     config = {
#         'instances': [self.MONGODB_CONFIG]
#     }
#     metrics_to_collect = {
#         'foo.bar': GAUGE,
#         'foobar.r': GAUGE,
#         'foobar.R': RATE,
#         'foobar.w': RATE,
#         'foobar.W': GAUGE,
#     }
#     self.load_check(config)
#     resolve_metric = self.check._resolve_metric
#
#     # Assert
#     self.assertEquals((GAUGE, 'mongodb.foo.bar'), resolve_metric('foo.bar', metrics_to_collect))  # noqa
#
#     self.assertEquals((RATE, 'mongodb.foobar.sharedps'), resolve_metric('foobar.R', metrics_to_collect))  # noqa
#     self.assertEquals((GAUGE, 'mongodb.foobar.intent_shared'), resolve_metric('foobar.r', metrics_to_collect))  # noqa
#     self.assertEquals((RATE, 'mongodb.foobar.intent_exclusiveps'), resolve_metric('foobar.w', metrics_to_collect))  # noqa
#     self.assertEquals((GAUGE, 'mongodb.foobar.exclusive'), resolve_metric('foobar.W', metrics_to_collect))  # noqa
#
# def test_state_translation(self):
#     """
#     Check that resolving replset member state IDs match to names and descriptions properly.
#     """
#     # Initialize check
#     config = {
#         'instances': [self.MONGODB_CONFIG]
#     }
#     self.load_check(config)
#
#     self.assertEquals('STARTUP2', self.check.get_state_name(5))
#     self.assertEquals('PRIMARY', self.check.get_state_name(1))
#
#     self.assertEquals('Starting Up', self.check.get_state_description(0))
#     self.assertEquals('Recovering', self.check.get_state_description(3))
#
#     # Unknown states:
#     self.assertEquals('UNKNOWN', self.check.get_state_name(500))
#     unknown_desc = self.check.get_state_description(500)
#     self.assertTrue(unknown_desc.find('500') != -1)
#
# def test_server_uri_sanitization(self):
#     # Initialize check
#     config = {
#         'instances': [self.MONGODB_CONFIG]
#     }
#     self.load_check(config)
#
#     _parse_uri = self.check._parse_uri
#
#     # Batch with `sanitize_username` set to False
#     server_names = (
#         ("mongodb://localhost:27017/admin", "mongodb://localhost:27017/admin"),
#         ("mongodb://user:pass@localhost:27017/admin", "mongodb://user:*****@localhost:27017/admin"),
#         ("mongodb://user:pass_%2@localhost:27017/admin", "mongodb://user:*****@localhost:27017/admin"), # pymongo parses the password as `pass_%2`
#         ("mongodb://user:pass_%25@localhost:27017/admin", "mongodb://user:*****@localhost:27017/admin"), # pymongo parses the password as `pass_%` (`%25` is url-decoded to `%`)
#         ("mongodb://user%2@localhost:27017/admin", "mongodb://user%2@localhost:27017/admin"), # same thing here, parsed username: `user%2`
#         ("mongodb://user%25@localhost:27017/admin", "mongodb://user%@localhost:27017/admin"), # with the current sanitization approach, we expect the username to be decoded in the clean name
#     )
#
#     for server, expected_clean_name in server_names:
#         _, _, _, _, clean_name, _ = _parse_uri(server, sanitize_username=False)
#         self.assertEquals(expected_clean_name, clean_name)
#
#     # Batch with `sanitize_username` set to True
#     server_names = (
#         ("mongodb://localhost:27017/admin", "mongodb://localhost:27017/admin"),
#         ("mongodb://user:pass@localhost:27017/admin", "mongodb://*****@localhost:27017/admin"),
#         ("mongodb://user:pass_%2@localhost:27017/admin", "mongodb://*****@localhost:27017/admin"),
#         ("mongodb://user:pass_%25@localhost:27017/admin", "mongodb://*****@localhost:27017/admin"),
#         ("mongodb://user%2@localhost:27017/admin", "mongodb://localhost:27017/admin"),
#         ("mongodb://user%25@localhost:27017/admin", "mongodb://localhost:27017/admin"),
#     )
#
#     for server, expected_clean_name in server_names:
#         _, _, _, _, clean_name, _ = _parse_uri(server, sanitize_username=True)
#         self.assertEquals(expected_clean_name, clean_name)

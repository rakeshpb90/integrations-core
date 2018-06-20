# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import mock
import pytest

from datadog_checks.errors import CheckException

@mock.patch("datadog_checks.openldap.openldap.os")
@mock.patch("datadog_checks.openldap.openldap.ldap3.core.tls.Tls")
@mock.patch("datadog_checks.openldap.openldap.ssl")
def test__get_tls_object(ssl_mock, ldap3_tls_mock, os_mock, check):
    # Check no SSL
    assert check._get_tls_object(None) is None

    # Check emission of warning, ssl validation none, and ca_certs_file
    ssl_params = {
        "key": None,
        "cert": None,
        "ca_certs": "foo",
        "verify": False,
    }
    os_mock.path.isdir.return_value = False
    os_mock.path.isfile.return_value = True
    log_mock = mock.MagicMock()
    check.log = log_mock
    check._get_tls_object(ssl_params)
    log_mock.warning.assert_called_once()
    assert "Incorrect configuration" in log_mock.warning.call_args[0][0]
    ldap3_tls_mock.assert_called_once_with(
        local_private_key_file=None,
        local_certificate_file=None,
        validate=ssl_mock.CERT_NONE,
        version=ssl_mock.PROTOCOL_SSLv23,
        ca_certs_file="foo",
    )

    # Check no warning, ssl validation required, and ca_certs_file none
    log_mock.reset_mock()
    ldap3_tls_mock.reset_mock()
    ssl_params = {
        "key": "foo",
        "cert": "bar",
        "ca_certs": None,
        "verify": True,
    }
    check._get_tls_object(ssl_params)
    log_mock.warning.assert_not_called()
    ldap3_tls_mock.assert_called_once_with(
        local_private_key_file="foo",
        local_certificate_file="bar",
        validate=ssl_mock.CERT_REQUIRED,
        version=ssl_mock.PROTOCOL_SSLv23,
        ca_certs_file=None,
    )

    # Check ca_certs_path
    os_mock.path.isdir.return_value = True
    os_mock.path.isfile.return_value = False
    ldap3_tls_mock.reset_mock()
    ssl_params = {
        "key": "foo",
        "cert": "bar",
        "ca_certs": "foo",
        "verify": True,
    }
    check._get_tls_object(ssl_params)
    ldap3_tls_mock.assert_called_once_with(
        local_private_key_file="foo",
        local_certificate_file="bar",
        validate=ssl_mock.CERT_REQUIRED,
        version=ssl_mock.PROTOCOL_SSLv23,
        ca_certs_path="foo",
    )

    # Check exception when invalid ca_certs_path
    with pytest.raises(CheckException):
        os_mock.path.isdir.return_value = False
        os_mock.path.isfile.return_value = False
        ssl_params = {
            "key": "foo",
            "cert": "bar",
            "ca_certs": "foo",
            "verify": True,
        }
        check._get_tls_object(ssl_params)


def test__get_instance_params(check):
    # Check default values
    instance = {
        "url": "foo",
    }
    assert check._get_instance_params(instance) == ("foo", None, None, None, [], ["url:foo"])

    # Check instance with no url raises
    with pytest.raises(CheckException):
        check._get_instance_params({})

    # Check ssl_params is None with non ldaps scheme
    instance = {
        "url": "ldap://foo",
        "ssl_key": "bar",
        "ssl_cert": "baz",
    }
    assert check._get_instance_params(instance) == ("ldap://foo", None, None, None, [], ["url:ldap://foo"])

    # Check all params ok
    url = "ldaps://url"
    user = "user"
    password = "pass"
    key = "key"
    cert = "cert"
    ca_certs = "capath"
    verify = False
    queries = ["query1", "query2"]
    tags = ["custom:tag"]
    ssl_params = {
        "key": key,
        "cert": cert,
        "ca_certs": ca_certs,
        "verify": verify,
    }
    instance = {
        "url": url,
        "username": user,
        "password": password,
        "ssl_key": key,
        "ssl_cert": cert,
        "ssl_ca_certs": ca_certs,
        "ssl_verify": verify,
        "custom_queries": queries,
        "tags": tags,
    }
    assert check._get_instance_params(instance) == (url, user, password, ssl_params,
                                                    queries, tags + ["url:ldaps://url"])

    # Check ssl_params default values
    url = "ldaps://url"
    ssl_params = {
        "key": None,
        "cert": None,
        "ca_certs": None,
        "verify": True,
    }
    instance = {
        "url": url,
    }
    assert check._get_instance_params(instance) == (url, None, None, ssl_params, [], ["url:ldaps://url"])

@mock.patch("datadog_checks.openldap.openldap.ldap3")
def test__perform_custom_queries(ldap3_mock, check):
    # Check name mandatory
    instance = {
        "url": "foo",
        "custom_queries": [{}]
    }
    log_mock = mock.MagicMock()
    check.log = log_mock
    conn_mock = ldap3_mock.Connection()
    _, _, _, _, queries, tags = check._get_instance_params(instance)
    check._perform_custom_queries(conn_mock, queries, tags, instance)
    conn_mock.search.assert_not_called()  # No search performed
    log_mock.error.assert_called_once()  # Error logged

    # Check search_base mandatory
    instance = {
        "url": "foo",
        "custom_queries": [{"name": "foo"}]
    }
    log_mock.reset_mock()
    _, _, _, _, queries, tags = check._get_instance_params(instance)
    check._perform_custom_queries(conn_mock, queries, tags, instance)
    conn_mock.search.assert_not_called()  # No search performed
    log_mock.error.assert_called_once()  # Error logged

    # Check search_filter mandatory
    instance = {
        "url": "foo",
        "custom_queries": [{"name": "foo", "search_base": "bar"}]
    }
    log_mock.reset_mock()
    _, _, _, _, queries, tags = check._get_instance_params(instance)
    check._perform_custom_queries(conn_mock, queries, tags, instance)
    conn_mock.search.assert_not_called()  # No search performed
    log_mock.error.assert_called_once()  # Error logged

    # Check query same username
    instance = {
        "url": "url",
        "username": "user",
        "password": "pass",
        "custom_queries": [{"name": "name", "search_base": "base", "search_filter": "filter"}]
    }
    log_mock.reset_mock()
    _, _, _, _, queries, tags = check._get_instance_params(instance)
    check._perform_custom_queries(conn_mock, queries, tags, instance)
    conn_mock.rebind.assert_called_once_with(user="user", password="pass", authentication=ldap3_mock.SIMPLE)
    conn_mock.search.assert_called_once_with("base", "filter", attributes=None)
    log_mock.error.assert_not_called()  # No error logged


def test__extract_common_name(check):
    # Check lower case and spaces converted
    dn = "cn=Max File Descriptors,cn=Connections,cn=Monitor"
    assert check._extract_common_name(dn) == "max_file_descriptors"

    # Check one cn
    dn = "cn=Max File Descriptors"
    assert check._extract_common_name(dn) == "max_file_descriptors"

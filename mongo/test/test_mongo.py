# # (C) Datadog, Inc. 2010-2017
# # All rights reserved
# # Licensed under Simplified BSD License (see LICENSE)
#
# # stdlib
# from types import ListType
# import time
# import unittest
#
# # 3p
# from mock import Mock
# from nose.plugins.attrib import attr
# import pymongo
#
# # project
# from checks import AgentCheck
# from tests.checks.common import AgentCheckTest, load_check
#
# PORT1 = 47017
# PORT2 = 47018
# MAX_WAIT = 150
#
# GAUGE = AgentCheck.gauge
# RATE = AgentCheck.rate
#

# @attr(requires='mongo')
# class TestMongo(unittest.TestCase):
#     def setUp(self):
#         server = "mongodb://localhost:%s/test" % PORT1
#         cli = pymongo.mongo_client.MongoClient(
#             server,
#             socketTimeoutMS=30000,
#             read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED,)
#
#         foos = []
#         for _ in range(70):
#             foos.append({'1': []})
#             foos.append({'1': []})
#             foos.append({})
#
#         bars = []
#         for _ in range(50):
#             bars.append({'1': []})
#             bars.append({})
#
#         db = cli['test']
#         db.foo.insert_many(foos)
#         db.bar.insert_many(bars)
#
#     def tearDown(self):
#         server = "mongodb://localhost:%s/test" % PORT1
#         cli = pymongo.mongo_client.MongoClient(
#             server,
#             socketTimeoutMS=30000,
#             read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED,)
#
#         db = cli['test']
#         db.drop_collection("foo")
#         db.drop_collection("bar")
#
#     def testMongoCheck(self):
#         self.agentConfig = {
#             'version': '0.1',
#             'api_key': 'toto'
#         }
#         self.config = {
#             'instances': [{
#                 'server': "mongodb://testUser:testPass@localhost:%s/test?authSource=authDB" % PORT1
#             }, {
#                 'server': "mongodb://testUser2:testPass2@localhost:%s/test" % PORT2
#             }]
#         }
#
#         # Test mongodb with checks.d
#         self.check = load_check('mongo', self.config, self.agentConfig)
#
#         # Run the check against our running server
#         self.check.check(self.config['instances'][0])
#
#         # Sleep for 1 second so the rate interval >=1
#         time.sleep(1)
#
#         # Run the check again so we get the rates
#         self.check.check(self.config['instances'][0])
#
#         # Metric assertions
#         metrics = self.check.get_metrics()
#         assert metrics
#         self.assertTrue(isinstance(metrics, ListType))
#         self.assertTrue(len(metrics) > 0)
#
#         metric_val_checks = {
#             'mongodb.asserts.msgps': lambda x: x >= 0,
#             'mongodb.fsynclocked': lambda x: x >= 0,
#             'mongodb.globallock.activeclients.readers': lambda x: x >= 0,
#             'mongodb.metrics.cursor.open.notimeout': lambda x: x >= 0,
#             'mongodb.metrics.document.deletedps': lambda x: x >= 0,
#             'mongodb.metrics.getlasterror.wtime.numps': lambda x: x >= 0,
#             'mongodb.metrics.repl.apply.batches.numps': lambda x: x >= 0,
#             'mongodb.metrics.ttl.deleteddocumentsps': lambda x: x >= 0,
#             'mongodb.network.bytesinps': lambda x: x >= 1,
#             'mongodb.network.numrequestsps': lambda x: x >= 1,
#             'mongodb.opcounters.commandps': lambda x: x >= 1,
#             'mongodb.opcountersrepl.commandps': lambda x: x >= 0,
#             'mongodb.oplog.logsizemb': lambda x: x >= 1,
#             'mongodb.oplog.timediff': lambda x: x >= 1,
#             'mongodb.oplog.usedsizemb': lambda x: x >= 0,
#             'mongodb.replset.health': lambda x: x >= 1,
#             'mongodb.replset.state': lambda x: x >= 1,
#             'mongodb.stats.avgobjsize': lambda x: x >= 0,
#             'mongodb.stats.storagesize': lambda x: x >= 0,
#             'mongodb.connections.current': lambda x: x >= 1,
#             'mongodb.connections.available': lambda x: x >= 1,
#             'mongodb.uptime': lambda x: x >= 0,
#             'mongodb.mem.resident': lambda x: x > 0,
#             'mongodb.mem.virtual': lambda x: x > 0,
#         }
#
#         tested_metrics = set()
#         for m in metrics:
#             metric_name = m[0]
#             if metric_name in metric_val_checks:
#                 self.assertTrue(metric_val_checks[metric_name](m[2]))
#                 tested_metrics.add(metric_name)
#
#         if len(metric_val_checks) - len(tested_metrics) != 0:
#             print "missing metrics: %s" % (set(metric_val_checks.keys()) - tested_metrics)
#         self.assertTrue(len(metric_val_checks) - len(tested_metrics) == 0)
#
#         # Run the check against our running server
#         self.check.check(self.config['instances'][1])
#         # Sleep for 1 second so the rate interval >=1
#         time.sleep(1)
#         # Run the check again so we get the rates
#         self.check.check(self.config['instances'][1])
#
#         # Service checks
#         service_checks = self.check.get_service_checks()
#         print service_checks
#         service_checks_count = len(service_checks)
#         self.assertTrue(isinstance(service_checks, ListType))
#         self.assertTrue(service_checks_count > 0)
#         self.assertEquals(len([sc for sc in service_checks if sc['check'] == self.check.SERVICE_CHECK_NAME]), 4, service_checks)
#         # Assert that all service checks have the proper tags: host and port
#         self.assertEquals(len([sc for sc in service_checks if "host:localhost" in sc['tags']]), service_checks_count, service_checks)
#         self.assertEquals(len([sc for sc in service_checks if "port:%s" % PORT1 in sc['tags'] or "port:%s" % PORT2 in sc['tags']]), service_checks_count, service_checks)
#         self.assertEquals(len([sc for sc in service_checks if "db:test" in sc['tags']]), service_checks_count, service_checks)
#
#         # Metric assertions
#         metrics = self.check.get_metrics()
#         assert metrics
#         self.assertTrue(isinstance(metrics, ListType))
#         self.assertTrue(len(metrics) > 0)
#
#         for m in metrics:
#             metric_name = m[0]
#             if metric_name in metric_val_checks:
#                 self.assertTrue(metric_val_checks[metric_name](m[2]))
#
#     def testMongoOldConfig(self):
#         conf = {
#             'init_config': {},
#             'instances': [
#                 {'server': "mongodb://localhost:%s/test" % PORT1},
#                 {'server': "mongodb://localhost:%s/test" % PORT2},
#             ]
#         }
#
#         # Test the first mongodb instance
#         self.check = load_check('mongo', conf, {})
#
#         # Run the check against our running server
#         self.check.check(conf['instances'][0])
#         # Sleep for 1 second so the rate interval >=1
#         time.sleep(1)
#         # Run the check again so we get the rates
#         self.check.check(conf['instances'][0])
#
#         # Metric assertions
#         metrics = self.check.get_metrics()
#         assert metrics
#         self.assertTrue(isinstance(metrics, ListType))
#         self.assertTrue(len(metrics) > 0)
#
#         metric_val_checks = {
#             'mongodb.connections.current': lambda x: x >= 1,
#             'mongodb.connections.available': lambda x: x >= 1,
#             'mongodb.uptime': lambda x: x >= 0,
#             'mongodb.mem.resident': lambda x: x > 0,
#             'mongodb.mem.virtual': lambda x: x > 0
#         }
#
#         for m in metrics:
#             metric_name = m[0]
#             if metric_name in metric_val_checks:
#                 self.assertTrue(metric_val_checks[metric_name](m[2]))
#
#         # Run the check against our running server
#         self.check.check(conf['instances'][1])
#         # Sleep for 1 second so the rate interval >=1
#         time.sleep(1)
#         # Run the check again so we get the rates
#         self.check.check(conf['instances'][1])
#
#         # Metric assertions
#         metrics = self.check.get_metrics()
#         assert metrics
#         self.assertTrue(isinstance(metrics, ListType))
#         self.assertTrue(len(metrics) > 0)
#
#         for m in metrics:
#             metric_name = m[0]
#             if metric_name in metric_val_checks:
#                 self.assertTrue(metric_val_checks[metric_name](m[2]))

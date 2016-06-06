from unittest import TestCase
from cloudcompose.datadog.monitoring.datadogcontroller import DatadogController
from cloudcompose.config import CloudConfig
from os.path import abspath, join, dirname

TEST_ROOT = abspath(join(dirname(__file__)))


# Run tests with py.test
# Must have DATADOG_APP_KEY and DATADOG_API_KEY in environment variables
class DatadogMonitoringTest(TestCase):
	def test_name(self):
		controller = self._datadog_controller('single_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		names = [monitor.get('name') for monitor in controller.monitor_data]
		self.assertEquals(['[single-test] MongoDB Single Test'], names)

		controller = self._datadog_controller('multi_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		names = [monitor.get('name') for monitor in controller.monitor_data]
		self.assertEquals(['Datadog Multi Test', 'Datadog Multi Test'], names)

	def test_monitor_tags(self):
		controller = self._datadog_controller('single_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		tagses = [monitor.get('tags') for monitor in controller.monitor_data]
		self.assertEquals([['clustername:single-test', 'monitor:mongodb-single-test']], tagses)
	
		controller = self._datadog_controller('multi_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		tagses = [monitor.get('tags') for monitor in controller.monitor_data]
		self.assertEquals([['clustername:multi-test', 'monitor:datadog-multi-1'], ['clustername:multi-test', 'monitor:datadog-multi-2']], tagses)

	def test_monitor_query(self):
		controller = self._datadog_controller('single_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		queries = [monitor.get('query') for monitor in controller.monitor_data]
		self.assertEquals(['max(last_1h):avg:mongodb.replset.replicationlag{clustername:single-test} by {nodeid} < -10'], queries)

		controller = self._datadog_controller('multi_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		queries = [monitor.get('query') for monitor in controller.monitor_data]
		self.assertEquals(['max(last_1h):avg:test{clustername:multi-test}' for i in range(2)], queries)

	def test_monitor_message(self):
		controller = self._datadog_controller('single_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		messages = [monitor.get('message') for monitor in controller.monitor_data]
		self.assertEquals(['Test Single @slack-arc-platform-ops'], messages)

		controller = self._datadog_controller('multi_monitor')
		[controller._resolve_monitor(mon) for mon in controller.monitor_data]
		messages = [monitor.get('message') for monitor in controller.monitor_data]
		self.assertEquals(['Test Multi 1 @slack-notify-one @slack-notify-two', 'Test Multi 2 @slack-notify-one @slack-notify-two'], messages)

	def _datadog_controller(self, config_dir):
		base_dir = join(TEST_ROOT, config_dir)
		cloud_config = CloudConfig(base_dir)
		return DatadogController(cloud_config)
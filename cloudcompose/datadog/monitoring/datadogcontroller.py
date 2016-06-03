from os import environ
from cloudcompose.util import require_env_var
import logging
from datadog import api, initialize

import pprint

TYPE = 'metric alert'

OPTIONS_NOTIFY_NO_DATA = {
	'notify_no_data': True,
	'no_data_timeframe': 480
}

OPTIONS_DEFAULT = {
	'notify_no_data': False
}



class DatadogController:
	def __init__(self, cloud_config):
		logging.basicConfig(level=logging.ERROR)
		self.logger = logging.getLogger(__name__)
		self.cloud_config = cloud_config
		self.config_data = cloud_config.config_data('datadog')
		self.cluster_name = cloud_config.config_data('datadog')['name']
		self.monitor_data = cloud_config.config_data('datadog')['monitors']
		# for monitor in self.monitor_data:
		# 	monitor['notify_no_data'] = monitor.get('notify_no_data', False)
		self.datadog_api_key = require_env_var('DATADOG_API_KEY')
		self.datadog_app_key = require_env_var('DATADOG_APP_KEY')
		self._datadog_init()

		self.pp = pprint.PrettyPrinter()
		# self.pp.pprint(self.monitor_data)


	def up(self):
		if not self.monitor_data:
			print 'No monitors defined\n\tDoing nothing'
		else:
			try:
				self._create_monitors()
			except Exception as e:
				raise

	def down(self):
		if not self.monitor_data:
			print 'No monitors defined\n\tDoing nothing'
		else:
			try:
				self._delete_monitors()
			except Exception as e:
				raise

	def _datadog_init(self):
		datadog_options = {
			'api_key': self.datadog_api_key,
			'app_key': self.datadog_app_key
		}

		initialize(**datadog_options)

	def _delete_monitors(self):
		for monitor in self.monitor_data:
			monitor_tag = monitor.get('tag')
			tags = [
				'clustername:{}'.format(self.cluster_name),
				'monitor:{}'.format(monitor_tag)
			]	
			match = self._get_existing_monitor(tags)

			if match:
				if 'id' in match:
					monitor_id = match['id']
					print 'Deleting monitor {}'.format(monitor_tag)
					api.Monitor.delete(monitor_id)
			# print '-'*16

	def _resolve_monitor(self, monitor):
		monitor['tags'] = ['clustername:{}'.format(self.cluster_name),
				'monitor:{}'.format(monitor.get('tag'))]
		monitor['query'] = monitor.get('query') % self.config_data
		cluster_prefix = self.config_data.get('use_cluster_prefix', True)
		if cluster_prefix:
			monitor['name'] = '[{}] {}'.format(self.cluster_name, monitor.get('name'))

		notified = self.config_data.get('notify', [''])
		monitor['message'] = '{} {}'.format(monitor.get('message'), ' '.join(notified))

		if monitor.get('notify_no_data', False):
			monitor['options'] = OPTIONS_NOTIFY_NO_DATA
		else:
			monitor['options'] = OPTIONS_DEFAULT

	def _create_monitors(self):
		for monitor in self.monitor_data:
			self._resolve_monitor(monitor)
			# self.pp.pprint(monitor)
			monitor_tag = monitor.get('tag')
			tags = monitor.get('tags')
			message = monitor.get('message')
			query = monitor.get('query')
			name = monitor.get('name')
			options = monitor.get('options')

			# notified = self.config_data.get('notify', [''])

			# message = '{} {}'.format(monitor_message, ' '.join(notified))

			# if monitor.get('notify_no_data', False):
			# 	options = OPTIONS_NOTIFY_NO_DATA
			# else:
			# 	options = OPTIONS_DEFAULT

			# name = '[{}] {}'.format(self.cluster_name, monitor_name)
			# tags = [
			# 	'clustername:{}'.format(self.cluster_name),
			# 	'monitor:{}'.format(monitor_tag)
			# ]
			# query = monitor_query % self.config_data

			old_monitor = self._get_existing_monitor(tags)

			if old_monitor:
				# Update rather than create
				monitor_id = old_monitor['id']
				print 'Updating monitor {}'.format(monitor_tag)
				api.Monitor.update(id=monitor_id, query=query, name=name, message=message, options=options, tags=tags)
			else:
				print 'Creating monitor {} for cluster {}.'.format(monitor_tag, self.cluster_name)
				api.Monitor.create(type=TYPE, query=query, name=name, message=message, options=options, tags=tags)
			# print query
			# print tags
			print '-'*16


	def _get_existing_monitor(self, tags):
		tags = sorted(tags)
		monitors = api.Monitor.get_all(type=TYPE)
		for monitor in monitors:
			if 'tags' in monitor:
				monitor_tags = sorted(monitor['tags'])
				if monitor_tags == tags:
					return monitor




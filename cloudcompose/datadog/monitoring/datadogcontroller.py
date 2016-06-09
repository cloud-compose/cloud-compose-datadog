from os import environ
from cloudcompose.util import require_env_var
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
		self.cloud_config = cloud_config
		self.config_data = cloud_config.config_data('datadog')
		self.cluster_name = cloud_config.config_data('datadog')['name']
		self.monitor_data = cloud_config.config_data('datadog')['monitors']
		self.default_options = cloud_config.config_data('datadog').get('options', {})

		self.datadog_api_key = require_env_var('DATADOG_API_KEY')
		self.datadog_app_key = require_env_var('DATADOG_APP_KEY')
		self._datadog_init()

		self.pp = pprint.PrettyPrinter(indent=2)


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
			# Search for the monitor using the tags that would have been created 
			#		through datadog monitors up
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

	def _resolve_monitor(self, monitor):
		# Take the monitor definition from the yaml and transform it 
		#		to what will be used to create the actual monitor
		monitor['tags'] = ['clustername:{}'.format(self.cluster_name),
				'monitor:{}'.format(monitor.get('tag'))]
		monitor['query'] = monitor.get('query') % self.config_data
		cluster_prefix = self.config_data.get('use_cluster_prefix', True)
		if cluster_prefix:
			monitor['name'] = '[{}] {}'.format(self.cluster_name, monitor.get('name'))

		notified = self.config_data.get('notify', [''])
		monitor['message'] = '{} {}'.format(monitor.get('message'), ' '.join(notified))

		# monitor['options'] = {}
		monitor['options'] = monitor.get('options', {}) # Instantiate it to an empty dict if it's not present
		for option in self.default_options:
			default_val = self.default_options[option]
			# Adds any default options not defined on the monitor level to the monitor
			monitor['options'][option] = monitor['options'].get(option, default_val) 

	def _create_monitors(self):
		for monitor in self.monitor_data:
			self._resolve_monitor(monitor)
			monitor_tag = monitor.get('tag')
			tags = monitor.get('tags')
			message = monitor.get('message')
			query = monitor.get('query')
			name = monitor.get('name')
			options = monitor.get('options')

			old_monitor = self._get_existing_monitor(tags)

			if old_monitor:
				# Update rather than create
				monitor_id = old_monitor['id']
				print 'Updating monitor {}:'.format(monitor_tag)
				response = api.Monitor.update(id=monitor_id, query=query, name=name, message=message, options=options, tags=tags)
				# self.pp.pprint(monitor)
				self.pp.pprint(response)
			else:
				print 'Creating monitor {} for cluster {}:'.format(monitor_tag, self.cluster_name)
				response = api.Monitor.create(type=TYPE, query=query, name=name, message=message, options=options, tags=tags)
				# self.pp.pprint(monitor)
				self.pp.pprint(response)
			print '-'*16


	def _get_existing_monitor(self, tags):
		tags = sorted(tags)
		monitors = api.Monitor.get_all(type=TYPE)
		for monitor in monitors:
			if 'tags' in monitor:
				monitor_tags = sorted(monitor['tags'])
				if monitor_tags == tags:
					return monitor




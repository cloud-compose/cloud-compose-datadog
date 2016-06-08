# Cloud Compose Datadog Plugin
The cloud compose datadog plugin simplifies the process of creating and deleting Datadog monitors. To use this plugin you will only need a single file:

* A cloud-compose.yml with desired configurations for your monitors

For an example project that uses Cloud Compose to create monitors see [Docker MongoDB](https://github.com/washingtonpost/docker-mongodb).

Once you have the configuration files, run the following commands to create the monitors:
```
cd my-configs
pip install cloud-compose cloud-compose-datadog
pip freeze > requirements.txt
cloud-compose datadog monitors up
```

And the following command to delete the monitors:
```
cloud-compose datadog monitors down
```

###Datadog API
This plugin uses the Datadog native API in order to create monitors, and thus requires the following environment variables:

1. DATADOG_API_KEY
1. DATADOG_APP_KEY

If you are using multiple Datadog accounts or want to be able to share those secrets easily, it is convenient to use [Envdir](https://pypi.python.org/pypi/envdir) to run the plugin

##Configuration
To understand the purpose of each part of the configuration file consider the following example with an explanation of each elelment:

###cloud-compose.yml
```yaml
datadog:
  name: ${CLUSTER_NAME}
  use_cluster_prefix: false
  notify:
    - '@slack-dev-ops'
  options: 
    notify_no_data: true
    no_data_timeframe: 480
  monitors:
    -
      tag: mongodb-host-status
      message: "The mongodb replication status on {{host.name}} indicates an error condition. See https://docs.mongodb.org/manual/reference/replica-states/ for details." 
      name: "MongoDB Host Status"
      query: 'max(last_1h):avg:mongodb.replset.state{clustername:%(name)s} by {host} > 2'
      options:
        notify_no_data: false
        notify_audit: true
    -
      tag: mongodb-backups-missing
      message: "Some mongodb backups are missing in the last hour. Check to see why the mongodb-backups container is not working on node-0 of the cluster." 
      name: "MongoDB Missing Backups"
      query: 'min(last_2h):min:mongodb.backups.missing{clustername:%(name)s} > 0'
```

####name
The ``name`` is the unique name of the cluster you will be creating the monitor on

####use_cluster_prefix (optional)
``use_cluster_prefix`` is a flag that, when enabled, will create monitors with the name format ``[${CLUSTER_NAME}] ${monitor_name}``. Defaults to true

####notify
A list of the people or channels you wish to ``notify`` when the monitor triggers an alert. Each element in the list will be appended to the end of each monitor's message for Datadog to use

####options (optional)*
Set the default ``options`` for each monitor that you want to create. Possible options can be found on the [Datadog API](http://docs.datadoghq.com/api/#monitors)

####monitors
The list of Datadog ``monitors`` you want to create

#####tag
The unique ``tag`` to attach to the monitor

####message
The ``message`` to be sent out to those specified when the monitor triggers an alert

####name
The ``name`` of the monitor to be created

####query
The ``query`` you want the monitor to listen to. In order to avoid conflicts with Datadog's own handlebars templating, the query string will be preformatted using Python 2's format string of the form ``%({{var}})s``, where {{var}} is defined under ``datadog`` in the yaml. For example, ``%(name)s`` will be replaced by ``${CLUSTER_NAME}``

####options (optional)*
Set the ``options`` for the individual monitor. Will be merged with the default options you have defined, but the individual monitor options will take precendence



\* For any given monitor you can have options defined at the top level, options defined at the individual level, both, or neither. If an option is not defined, it will have the default value according to the [Datadog API](http://docs.datadoghq.com/api/#monitors)

## Contributing 
To work on the code locally, checkout both cloud-compose and cloud-compose-datadog to the same parent directory. Then use a virtualenv and pip install editable to start working on them locally.
```
mkvirtualenv cloud-compose
pip install --editable cloud-compose
pip install --editable cloud-compose-datadog
```

Make sure to add unit tests for new code. You can run them using the standard setup tools command:

```
python setup.py test
``` 
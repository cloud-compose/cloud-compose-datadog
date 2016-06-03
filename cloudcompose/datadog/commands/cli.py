import click
from cloudcompose.datadog.monitoring.datadogcontroller import DatadogController
from cloudcompose.config import CloudConfig
from cloudcompose.exceptions import CloudComposeException

@click.group()
def cli():
    pass

@cli.command()
@click.argument('mode')
def monitors(mode):
    """
    Create or delete Datadog monitors defined in cloudcompose.yml
    """
    cloud_config = CloudConfig()
    datadog_controller = DatadogController(cloud_config)
    if mode.lower() == 'up':
        datadog_controller.up()
    elif mode.lower() == 'down':
        datadog_controller.down()
    else:
        raise CloudComposeException('{} not a valid argument'.format(mode))

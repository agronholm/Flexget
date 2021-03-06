import logging

from flexget import plugin
from flexget.event import event
from flexget.plugin import PluginError

log = logging.getLogger('list_add')


class ListAdd(object):
    schema = {
        'type': 'array',
        'items': {
            'allOf': [
                {'$ref': '/schema/plugins?group=list'},
                {
                    'maxProperties': 1,
                    'error_maxProperties': 'Plugin options within list_add plugin must be indented 2 more spaces than '
                                           'the first letter of the plugin name.',
                    'minProperties': 1
                }
            ]
        }
    }

    def on_task_start(self, task, config):
        for item in config:
            for plugin_name, plugin_config in item.iteritems():
                try:
                    thelist = plugin.get_plugin_by_name(plugin_name).instance.get_list(plugin_config)
                except AttributeError:
                    raise PluginError('Plugin %s does not support list interface' % plugin_name)
                if thelist.immutable:
                    raise plugin.PluginError(thelist.immutable)

    def on_task_output(self, task, config):
        for item in config:
            for plugin_name, plugin_config in item.iteritems():
                if task.manager.options.test:
                    log.info('Would add accepted items to `%s` outside of --test mode.' % plugin_name)
                    continue
                thelist = plugin.get_plugin_by_name(plugin_name).instance.get_list(plugin_config)
                thelist |= task.accepted


@event('plugin.register')
def register_plugin():
    plugin.register(ListAdd, 'list_add', api_ver=2)

from DivvyPlugins.plugin_metadata import PluginMetadata

class metadata(PluginMetadata):
    version = '1.0'
    last_updated_date = '2016-01-28'
    author = 'Divvy Cloud Corp.'
    nickname = 'Slack Integration'
    default_language_description = 'Collection of slack integrations'
    support_email = 'support@divvycloud.com'
    support_url = 'http://support.divvycloud.com'
    main_url = 'http://www.divvycloud.com'
    managed = True


def load():
    pass


def unload():
    pass

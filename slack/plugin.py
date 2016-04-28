import json

import requests
from flask import Blueprint, request
from jinja2 import Template
from DivvyUtils.field_definition import StringField
from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyResource.Resources      import DivvyPlugin
from DivvyPlugins.settings        import GlobalSetting

from DivvyBotfactory.registry import BotFactoryAction, ActionRegistry

class metadata(PluginMetadata):
    version                       = '1.0'
    last_updated_date             = '2016-04-30'
    author                        = 'Divvy Cloud Corp.'
    nickname                      = 'Slack Integration'
    default_language_description  = 'Collection of slack integrations'
    support_email                 = 'support@divvycloud.com'
    support_url                   = 'http://support.divvycloud.com'
    main_url                      = 'http://www.divvycloud.com'
    managed                       = True


blueprint = Blueprint('slack', __name__, static_folder='html', template_folder='html')


#Setting Names
PREFIX           = DivvyPlugin.get_current_plugin().name
APIKEY           = PREFIX + '.apiKey'
CHANNEL          = PREFIX + '.channel'
USERNAME         = PREFIX + '.username'


#Plugin reference
PLUGIN_REF = DivvyPlugin.get_current_plugin()


#Register Global Settings
apiKey = GlobalSetting(
    name         = APIKEY,
    display_name = 'Slack API key',
    type_hint    = 'string',
    description  = 'This apiKey allows a user to access slack integration')


channel = GlobalSetting(
    name         = CHANNEL,
    display_name = 'Default Slack channel',
    type_hint    = 'string',
    description  = 'This is where slack will post messages')


username = GlobalSetting(
    name         = USERNAME,
    display_name = 'Default Slack username',
    type_hint    = 'string',
    description  = 'This is the username messages are sent from')


def send_slack(message, channel=None, username=None):
    """Send a message to slack."""
    api_key = apiKey.get_for_resource(PLUGIN_REF)
    if api_key:
        payload = {
            'channel': channel or channel.get_for_resource(PLUGIN_REF),
            'username': username or username.get_for_resource(PLUGIN_REF),
            'text': message
        }

        data = json.dumps(payload)
        response = requests.post(apiKey, data=data)
    
        return response.content
    else:
        pass


def botfactory_slack(event, current_bot, settings):
    message_raw = Template(settings.get('message', 'Error: message not configured'))
    message = message_raw.render(event=event)
    
    return send_slack(message, channel=settings.get('channel'), username=settings.get('username'))


ACTIONS = [
    BotFactoryAction(
        uid='slack.send_slack',
        name='Send Slack Message',
        description='Sends message to slack that is \
                    formatted with resource attributes using Jinja2 templates. Eg. {{event.resource.name}}',
        author='DivvyCloud Inc.',
        supported_resources=[],
        settings_config=[
            StringField(
                name='channel',
                display_name='Slack Channel',
                description="Slack Channel from which the message should be sent"),
            StringField(
                name='username',
                display_name='Slack Username',
                description="Slack Username from which the message should be sent"),
            StringField(
                name='message',
                display_name='Message Body',
                description="Contents of the message. Jinja2 formatting is allowed")
        ],
        function=botfactory_slack
    )
]


def load():
    ActionRegistry().registry.register(ACTIONS)


def unload():
    ActionRegistry().registry.unregister(ACTIONS)

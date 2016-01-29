import json

import requests
from flask import Blueprint, request

from DivvyPlugins.hookpoints import hookpoint
from DivvyPlugins.plugin_helpers import register_api_blueprint, unregister_api_blueprints
from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyUtils.flask_helpers import JsonResponse
from DivvyResource.Resources import DivvyPlugin
from DivvyPlugins.settings import GlobalSetting


class metadata(PluginMetadata):
    version                       = '1.0'
    last_updated_date             = '2016-01-28'
    author                        = 'Divvy Cloud Corp.'
    nickname                      = 'Slack Integration'
    default_language_description  = 'Collection of slack integrations'
    support_email                 = 'support@divvycloud.com'
    support_url                   = 'http://support.divvycloud.com'
    main_url                      = 'http://www.divvycloud.com'
    managed                       = True

blueprint = Blueprint('slack', __name__, static_folder='html', template_folder='html')

#Setting Names
PREFIX   = DivvyPlugin.get_current_plugin().name
APIKEY   = PREFIX + '.apiKey'
CHANNEL  = PREFIX + '.channel'
USERNAME = PREFIX + '.username'

#Register Global Settings
apiKey = GlobalSetting(
    name         = APIKEY,
    display_name = 'Slack API key',
    type_hint    = 'string',
    description  = 'This apiKey allows a user access slack integration')

channel = GlobalSetting(
    name         = '#'+CHANNEL,
    display_name = 'Slack channel name',
    type_hint    = 'string',
    description  = 'This channel is where slack will post messages')

username = GlobalSetting(
    name         = USERNAME,
    display_name = 'Slack username',
    type_hint    = 'string',
    description  = 'This will be the username that messages are sent from')


@blueprint.route('/', methods=['POST'])
def send_to_slack():
    """Send a message to slack."""
    #get message
    message = json.loads(request.data)

    #get plugin reference
    plugin_ref = DivvyPlugin.get_current_plugin();

    # Form slack payload
    payload = {
        'channel': channel.get_for_resource(plugin_ref),
        'username': username.get_for_resource(plugin_ref),
        'text': message['text']
    }

    data = json.dumps(payload)

    response = requests.post(apiKey.get_for_resource(plugin_ref), data=data)

    return JsonResponse({'Response': response.content})


# Needs to be scoped down! Will span slack general channel -Peter
# @hookpoint('divvycloud.instance.modified')
# def hamster(resource, old_resource_data, user_resource_id=None):
#     payload = {
#         'channel': '#general',
#         'username': 'annagoldberg',
#         'text': "this is a test on modified of an instance"
#     }
#
#     data = json.dumps(payload)
#     return requests.post("https://hooks.slack.com/services/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", data=data)


def load():
    register_api_blueprint(blueprint)


def unload():
    unregister_api_blueprints()


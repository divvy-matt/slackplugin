import json

import requests
from flask import Blueprint, request

from DivvyPlugins.hookpoints      import hookpoint
from DivvyPlugins.plugin_helpers  import register_api_blueprint, unregister_api_blueprints
from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyUtils.flask_helpers     import JsonResponse
from DivvyResource.Resources      import DivvyPlugin
from DivvyPlugins.settings        import GlobalSetting


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
MESSAGE  = PREFIX + '.message'
#Plugin reference
PLUGIN_REF = DivvyPlugin.get_current_plugin()

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

message = GlobalSetting(
    name         = MESSAGE,
    display_name = 'Messagy body',
    type_hint    = 'string',
    description  = 'This is a default message body'
)

def send_to_slack(channel,username,message,apiKey):
    """Send a message to slack."""

    # Form slack payload
    payload = {
        'channel': channel,
        'username': username,
        'text': message
    }

    data = json.dumps(payload)
    response = requests.post(apiKey, data=data)
    return response.content

@blueprint.route('/', methods=['POST'])
def send_slack():
    """Send a message to slack by request"""
    payload        = json.loads(request.data)
    channel_name   = payload.get('channel', channel.get_for_resource(PLUGIN_REF))
    user_name      = payload.get('username', username.get_for_resource(PLUGIN_REF))
    message_body   = payload.get('text', message.get_for_resource(PLUGIN_REF))
    api_key        = payload.get('apiKey', apiKey.get_for_resource(PLUGIN_REF))

    response = send_to_slack(channel_name, user_name, message_body, api_key)
    return JsonResponse({'Response': response})

# Needs to be scoped down! Will span slack channel -Peter
# @hookpoint('divvycloud.instance.modified')
# def send_change_to_slack(resource, old_resource_data, user_resource_id=None):
#     """Send a message to slack if resource has changed."""
#     #pass searchID into function?
#     # if(!resource.resourceID == search_ID ):
#     #     return
#     #
#
#     payload = {
#         'channel':  channel.get_for_resource(plugin_ref),
#         'username': username.get_for_resource(plugin_ref),
#         'text':     'this is a modified instance'
#     }
#
#     data = json.dumps(payload)
#     return requests.post("https://hooks.slack.com/services/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", data=data)


# @BotFunctionRegistry.action(
#     display_name="Send Slack Message",
#     unique_name="divvy.send_slack",
#     input_types=["instance"],
#     setting_definitions=[
#         StringField(
#             name='channel',
#             display_name='Slack Channel',
#             description="Slack Channel from which the message should be sent"),
#         StringField(
#             name='username',
#             display_name='Slack Username',
#             description="Slack Username from which the message should be sent"),
#         StringField(
#             name='message',
#             display_name='Message Body',
#             description="Contents of the message which should be sent"),
#         StringField(
#             name='apiKey',
#             display_name='Slack API key',
#             description="Slack API key to allow slack integration"),
#     ])
# def slack_message(resource, current_bot, settings):
#     send_to_slack(channel=settings['channel'].format(resource=resource),
#                username=settings['username'].format(resource=resource),
#                message=settings['subject'].format(resource=resource),
#                apiKey=settings['apiKey'].format(resource=resource),
#                botFactory=True)
#     print 'slack message sent!'

def load():
    register_api_blueprint(blueprint)


def unload():
    unregister_api_blueprints()


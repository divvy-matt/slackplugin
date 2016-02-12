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
PREFIX           = DivvyPlugin.get_current_plugin().name
APIKEY           = PREFIX + '.apiKey'
CHANNEL          = PREFIX + '.channel'
USERNAME         = PREFIX + '.username'
MESSAGE          = PREFIX + '.message'
RESOURCEID       = PREFIX + '.resourceID'
RESOURCETYPE     = PREFIX + '.resourceType'
RESOURCENAME     = PREFIX + '.resourceName'
RESOURCELOCATION = PREFIX + '.resourceLocation'
ORIGINID         = PREFIX + '.originID'
RESOURCETAGKEY   = PREFIX + '.resourceTagKey'

#Plugin reference
PLUGIN_REF = DivvyPlugin.get_current_plugin()

#Register Global Settings
apiKey = GlobalSetting(
    name         = APIKEY,
    display_name = 'Slack API key',
    type_hint    = 'string',
    description  = 'This apiKey allows a user to access slack integration')

channel = GlobalSetting(
    name         = '#'+CHANNEL,
    display_name = 'Slack channel name',
    type_hint    = 'string',
    description  = 'This is where slack will post messages')

username = GlobalSetting(
    name         = USERNAME,
    display_name = 'Slack username',
    type_hint    = 'string',
    description  = 'This is the username messages are sent from')

message = GlobalSetting(
    name         = MESSAGE,
    display_name = 'Message body',
    type_hint    = 'string',
    description  = 'This is a default message body'
)

resourceID = GlobalSetting(
    name         = RESOURCEID,
    display_name = 'Resource ID',
    type_hint    = 'string',
    description  = 'The resource ID'
)

resourceType = GlobalSetting(
    name         = RESOURCETYPE,
    display_name = 'Resource type',
    type_hint    = 'string',
    description  = 'The resource type'
)

resourceName = GlobalSetting(
   name          = RESOURCENAME,
   display_name  = 'Resource name',
   type_hint     = 'string',
   description   = 'The resource name'
)

resourceTagKey = GlobalSetting(
   name          = RESOURCETAGKEY,
   display_name  = 'Resource tag key',
   type_hint     = 'string',
   description   = 'Resource tag key'
)

originID = GlobalSetting(
    name         = ORIGINID,
    display_name = 'Origin ID',
    type_hint    = 'string',
    description  = 'The origin ID'
)

resourceLocation = GlobalSetting(
   name          = RESOURCELOCATION,
   display_name  = 'Resource location',
   type_hint     = 'string',
   description   = 'The resource location'
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

def resource_match(resource):
    #get user input for resource criteria
    resource_id       = resourceID.get_for_resource(PLUGIN_REF)
    resource_location = resourceLocation.get_for_resource(PLUGIN_REF)
    origin_id         = originID.get_for_resource(PLUGIN_REF)
    resource_type     = resourceType.get_for_resource(PLUGIN_REF)
    resource_name     = resourceName.get_for_resource(PLUGIN_REF)
    resource_tag_key  = resourceTagKey.get_for_resource(PLUGIN_REF)

    return resource.resource_id.to_string()    == resource_id \
       or resource.instance_id                 == origin_id \
       or resource.region_name                 == resource_location \
       or resource.get_resource_name           == resource_name \
       or resource.get_instance_type()         == resource_type\
       or resource.get_tag(resource_tag_key)


@hookpoint('divvycloud.instance.created')
@hookpoint('divvycloud.instance.modified')
def send_change_to_slack(resource, old_resource_data, user_resource_id=None):
    """Send a message to slack if resource has changed."""

    #user input for slack messaging
    channel_name   = channel.get_for_resource(PLUGIN_REF)
    user_name      = username.get_for_resource(PLUGIN_REF)
    message_body   = 'This is a modified instance of reference:' + resource.resource_id.to_string()
    api_key        = apiKey.get_for_resource(PLUGIN_REF)

    #if any of the criteria match send a message
    if resource_match(resource) :
        send_to_slack(channel_name, user_name, message_body, api_key)



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


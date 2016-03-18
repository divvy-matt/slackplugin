
import json

import requests
from flask import Blueprint, request
from jinja2 import Template

from DivvyPlugins.hookpoints      import hookpoint
from DivvyPlugins.plugin_helpers  import register_api_blueprint, unregister_api_blueprints
from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyUtils.flask_helpers     import JsonResponse
from DivvyResource.Resources      import DivvyPlugin
from DivvyPlugins.settings        import GlobalSetting
from DivvyUtils.field_definition import StringField, MultiSelectionField, FieldOptions
from DivvyUtils.mail import send_email
from DivvyWorkers.OnDemand import InstanceLifecycle


import sys
sys.path.append('/Users/chancecard88/Code/plugins/botfactory/cooked')

from botfactory import registry

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
    print("about to send the message: " + message + " part II!")
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
    resource_id             = resourceID.get_for_resource(PLUGIN_REF)
    resource_location       = resourceLocation.get_for_resource(PLUGIN_REF)
    origin_id               = originID.get_for_resource(PLUGIN_REF)
    resource_type           = resourceType.get_for_resource(PLUGIN_REF)
    resource_name           = resourceName.get_for_resource(PLUGIN_REF)
    resource_tag_key        = resourceTagKey.get_for_resource(PLUGIN_REF)
    resource_tag_key_match  = False

    #if a tag key was entered in settings pass it to get_tag
    if resource_tag_key != '':
       try:
        resource.get_tag(resource_tag_key)
        resource_tag_key_match = True
       except:
        pass

    return resource.resource_id.to_string()    == resource_id \
       or resource.instance_id                 == origin_id \
       or resource.region_name                 == resource_location \
       or resource.get_resource_name()           == resource_name \
       or resource.get_instance_type()         == resource_type \
       or resource_tag_key_match


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

def slackMessage(resource, current_bot, settings):
    print("about to send a slack message in bot factory")
    #send the message to slack
    send_to_slack(channel=settings['channel'],
                  username=settings['username'],
                  message=Template(settings['message']).render(resource=resource),
                  api_key=settings['api_key'])

def stop_instance(resource, current_bot, settings):
    InstanceLifecycle.StopInstanceJob(resource.resource_id, None).run_job().result(timeout=60)


def log(resource, current_bot, settings):
    print(resource.resource_id, "Log from botfactory")


ACTIONS = [
    registry.BotFactoryAction(
        uid='divvy.action.log',
        name='Log line',
        description='Log info message for development',
        author='DivvyCloud Inc.',
        supported_resources=[],
        settings_config=[],
        function=log
    ),
    registry.BotFactoryAction(
        uid='divvy.action.instance.start',
        name='Start Instance',
        description='Attempts Instance Start life cycle action. Action is dependant on resource state.',
        author='DivvyCloud Inc.',
        supported_resources=[],
        settings_config=[],
        function=stop_instance
    ),
    registry.BotFactoryAction(
        uid='divvy.action.send_slack_message',
        name='Send Slack Message',
        description='Sends slack message and allows slack message body to be \
                    formatted with resource attributes. Eg. {resource.<attr_name>}',
        author='DivvyCloud Inc.',
        supported_resources=[],
        settings_config=[
            StringField(
                name='api_key',
                display_name='slack api key',
                description='The api Key allows a user to access slack integration',
                options=FieldOptions.REQUIRED),
            StringField(
                name='username',
                display_name='Slack username',
                description='This is the username messages are sent from',
                options=FieldOptions.REQUIRED),
            StringField(
                name='channel',
                display_name='Slack channel name',
                description="Channel to post slack messages",
                options=FieldOptions.REQUIRED),
            StringField(
                name='message',
                display_name='Message Body',
                description="Contents of the message which should be sent",
                options=FieldOptions.REQUIRED)
        ],
        function=slackMessage
    )
]

def load():
    register_api_blueprint(blueprint)
    registry.ActionRegistry().registry.register(ACTIONS)



def unload():
    unregister_api_blueprints()
    registry.ActionRegistry().registry.unregister(ACTIONS)


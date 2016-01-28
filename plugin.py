import json

import requests
from flask import Blueprint, request

from DivvyPlugins.plugin_helpers import register_api_blueprint, unregister_api_blueprints
from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyUtils.flask_helpers import JsonResponse


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

blueprint = Blueprint('slack', __name__, static_folder='html', template_folder='html')

@blueprint.route('/', methods=['GET'])
def send_to_slack():
    """
    Send a message to slack.
    """
    reqobject = request
    # Form slack payload
    payload = {
        'channel': '#general',
        'username': 'annagoldberg',
        'text': reqobject.args['foo']
    }

    data = json.dumps(payload)
    response = requests.post("https://hooks.slack.com/services/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", data=data)

    return JsonResponse({'HamBacon': response.content})


def load():
    register_api_blueprint(blueprint)


def unload():
    unregister_api_blueprints()


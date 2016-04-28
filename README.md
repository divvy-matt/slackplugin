# DivvyCloud Simple Slack Integration
![divycloud_slack_v2](https://cloud.githubusercontent.com/assets/2007892/14179732/3fd6c788-f72e-11e5-9feb-9083ef8c674f.png)

Send messages to Slack using Slack's [Incoming Webhooks API](https://api.slack.com/incoming-webhooks "Slack API docs").

## Slack Setup
Login to Slack and go to Custom Integrations > Incoming Webhooks then click "Add configuration". This will allow you to generate a URL which can be used to POST messages to the channels of your choosing.

## DivvyCloud Setup
Copy the `slackplugin/slack` directory into your plugins directory. DivvyCloud will detect and load it.

Login to DivvyCloud and visit the Plugins page, select "Manage Plugin" for the SlackPlugin. 

Go to the Global Settings tab and enter the Slack API key URL. You can optionally set a default channel and user to post from.

## BotFactory Usage
The Slack plugin depends on the Botfactory plugin being loaded. 

From the main menu, go to the Botfactory page. Select 'create bot' and from there you can select "Send Slack" as an action to the bot. Your options are 1) message, 2) channel and 3) username. 

The message string uses [Jinja2 templates](http://jinja.pocoo.org/docs/dev/) with the Botfactory event object available to format the message. 

```
# Event properties
event.hookpoint_str     # String: eg. divvycloud.resource.modified
event.resource          # Object: DivvyCloud resource. Attributes accessed via dot notation. See Jinja2 documentation
event.resource_type     # String: DivvyCloud resource type as string
event.old_resource_data # Object: DivvyCloud resource. Only available on divvycloud.resource.modified

# Example
"Hey slack channel, Divvy resource {{ event.resource.name }} changed!"
```

## Python Usage (coming soon!)
If the plugin in loaded as an egg file you can import the send_slack function to used in your python plugin. Loading as an egg file guarantees load time order and will always be avaible. 
```
from plugins.slack import send_slack
# Function signature
def send_slack(message, channel=None, username=None):
  # sends your message
```
Both Channel and Username will default to the global settings if not specified.

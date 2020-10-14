
import sys
import os
import requests
import json
from requests.auth import HTTPBasicAuth
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import jinja2
from flask import Flask, render_template
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from creds import CLIENT_ID, CLIENT_SECRET, TEAMS_BOT_EMAIL, TEAMS_BOT_TOKEN,TEAMS_BOT_APP_NAME
except:
    print("Error reading credentials. Check credentials in creds.py file.\n")
    exit() 

try:
    json_data = json.loads((requests.get("http://127.0.0.1:4040/api/tunnels")).content)
    #print(json_data)
    ngrok_url = json_data['tunnels'][1]['public_url']
    print(ngrok_url)
    TEAMS_BOT_URL = ngrok_url
except:
    print("Error getting ngrok url. Have you started ngrok?\n")
    exit()


# Retrieve required details from environment variables
# Bot Details
bot_email = TEAMS_BOT_EMAIL
teams_token = TEAMS_BOT_TOKEN
bot_url = TEAMS_BOT_URL
bot_app_name = TEAMS_BOT_APP_NAME

# Who is is allowed to interact with the bot
approved_users = [
    "omer.chohan@bt.com",
]

# Create a Bot Object
# Note: debug mode prints out more details about processing to terminal
# Note: add approved_users=approved_users to restrict who can interact with the bot
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True
)

# Create a function to respond to messages that lack any specific command
# The greeting will be friendly and suggest how to interact with the bot
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)
#    print("<<<<<<<<<<<\n {} \n>>>>>>>>>>".format(sender))
    
    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}  \U0001F44B\n".format(sender.displayName)
    response.markdown += "My name is TAC API Runner, you can call me @tacbot."
    response.markdown += "\n\nSee what I can do by asking for **/help**."
    return response

def bot_help(incoming_msg):
    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "I can help you with below commands:"
    response.markdown += "\n\n**/help**  - Print this help message. "
    response.markdown += "\n**/sn2info** 'serial'  - Get Cisco contract cover info."
    response.markdown += "\n**/vul** 'version'  - Check Cisco PSIRT openVuln API with version.\n"
    return response

def get_token(clientid=CLIENT_ID,clientsec=CLIENT_SECRET):
    token_url = "https://cloudsso.cisco.com/as/token.oauth2"
    token_response = requests.post(token_url, verify=False, data={"grant_type": "client_credentials"},
                             headers={"Content-Type": "application/x-www-form-urlencoded"},
                             params={"client_id": clientid, "client_secret": clientsec})
    access_token = token_response.json()['access_token']
    return access_token

def get_sn2info(serial):
    token = get_token()
    status_url = "https://api.cisco.com/sn2info/v2/coverage/status/serial_numbers/"+serial+"?page_index=1"
    headers = {"authorization": "Bearer " + token, "accept": "application/json",}
    status_response = requests.get(status_url, headers=headers)
    if (status_response.status_code == 200):
        info = json.loads(status_response.text)

    return info

def sn2info(incoming_msg):
    response = Response()
    print(incoming_msg)
    serial = bot.extract_message(
        "/sn2info", incoming_msg.text).strip()
    print("Serial: {}".format(serial))
    if len(serial) != 0:
        response.markdown = "Please wait while I fetch the data \U0001F557\n"
        info = get_sn2info(serial)
        print("<<<<<<<<<<<\n {} \n>>>>>>>>>>".format(info))
        response.markdown = "**Serial to Info Status**\n\n"
        for i in info['serial_numbers']:
            response.markdown += "Serial No.:  {}\n".format(i['sr_no'])
            response.markdown += "Covered:  {}\n".format(i['is_covered'])
            response.markdown += "Cover End:  {}\n".format(i['coverage_end_date'])
    else:
        response.markdown = "No serial number supplied.\n\n"
        response.markdown += sn2info_help

    return response

# Create help message for client command
sn2info_help = "Check Cisco contract status.\n"
sn2info_help += "Example: **/sn2info** FCZ123456AB\n"


def get_advisories(ver,clientid=CLIENT_ID,clientsec=CLIENT_SECRET):
    token = get_token()
    headers = {"authorization": "Bearer " + token, "accept": "application/json",}
    adv_url = "https://api.cisco.com/security/advisories/iosxe/?version={0}".format(ver)
    #print("<<<<<<<<<{}>>>>>>>>>>".format(url))
    response = requests.get(adv_url, verify=False, headers=headers)

    if response.status_code == 200:
        # Uncomment to see the full dict return by the API
        #print(json.loads(response.text))
        advisory_dict = {"release": ver, "advisories": []}
        #advisory_repsonse = json.loads(response.text)["advisories"]
        advisory_dict["advisories"] = build_advisories_dict(json.loads(response.text)["advisories"])
        # Uncomment to debug the data returned by  build_advisories_dict()
        #print(advisory_repsonse)
        return advisory_dict

    return {"release": ver, "advisories": [], "state": "ERROR", "detail": response.status_code}

def build_advisories_dict(advisories):
    adv_list = []
    for adv in advisories:
        adv_dict = dict()
        adv_dict["advisory_id"] = adv["advisoryId"] if "advisoryId" in adv else "Unknown"
        adv_dict["advisory_title"] = adv["advisoryTitle"] if "advisoryTitle" in adv else "Unknown"
        adv_dict["bug_ids"] = adv["bugIDs"] if "bugIDs" in adv else "Unknown"
        adv_dict["cves"] = adv["cves"] if "cves" in adv else "Unknown"
        adv_dict["cvssBaseScore"] = adv["cvssBaseScore"] if "cvssBaseScore" in adv else "Unknown"
        adv_dict["first_fixed"] = adv["firstFixed"] if "firstFixed" in adv else "Unknown"
        adv_dict["firstPublished"] = adv["firstPublished"] if "firstPublished" in adv else "Unknown"
        #adv_dict["productNames"] = adv["productNames"] if "productNames" in adv else "Unknown"
        adv_dict["sir"] = adv["sir"] if "sir" in adv else "Unknown"
        adv_list.append(adv_dict)
    #print(">>>>",adv_list)
    return adv_list

def advisory(incoming_msg):
    response = Response()
    print(incoming_msg)
    version = bot.extract_message(
        "/vul", incoming_msg.text).strip()
    print("Version: {}".format(version))
    if len(version) != 0:
        response.markdown = "Please wait while I fetch the data \U0001F557\n"
        info = get_advisories(version)

        if len(info["advisories"]) == 0:
            message = "openVuln API returned {0}. No advisories found.".format(info["detail"]) if info["state"] == "ERROR" \
                else "None found"

            print("{0}".format(message))
            response.markdown = "{0}".format(message)
        else:

            #print("<<<<<<<<<<<\n {} \n>>>>>>>>>>".format(info))
            fixed_releases = []
            #print((info))
            formatted_text = ""
            for item in info["advisories"]:
                formatted_text += "**ID:** {0} - {1}\n**First Published:** {2}\n**First fixed:** {3}\n**Bug IDs:** {4}\n**CVE ID:** {5}\n**Score:** {6} - **Severity:** {7}\n".format(item["advisory_id"], 
                                                     item["advisory_title"],
                                                     item["firstPublished"],
                                           ", ".join(item["first_fixed"]), 
                                           ", ".join(item["bug_ids"]),
                                           ", ".join(item["cves"]),
                                                     item["cvssBaseScore"],
                                                     item["sir"],)
                fixed_releases += item["first_fixed"]
                print(">>>>>>>.",fixed_releases)
            print(formatted_text)
            response.markdown = "**Cisco PSIRT openVuln API**\n\n"     
            response.markdown += formatted_text
        
            response.markdown += "\n**Advisories Published:** {0}\n".format(len(info["advisories"]))
            response.markdown += "**Minimum Suggested Release:** {0}\n".format(sorted(fixed_releases)[len(fixed_releases)-1])
        
    else:
        response.markdown = "No version supplied.\n\n"
        response.markdown += vul_help
    
    return response

vul_help = "Check Cisco PSIRT openVuln API with version.\n"
vul_help += "Example: **/vul** 16.12.4a\n"


# Set the bot greeting
bot.set_greeting(greeting)

# Add commands to the bot
bot.add_command(
    "/help", "Get Help.", bot_help
)

bot.add_command(
    "/sn2info", sn2info_help, sn2info
)

bot.add_command(
    "/vul", vul_help, advisory
)

# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")

if __name__ == "__main__":
    bot.run(host="0.0.0.0", port=7001)

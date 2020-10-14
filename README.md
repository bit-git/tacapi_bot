[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/bit-git/tacapi_bot)
# tacapi_bot
Simple WebEx Teams chatbot to query Cisco Serial Number to Info Status and Cisco PSRIT openVuln APIs</br>
Reference: https://pypi.org/project/webexteamsbot/#description

![bot](https://github.com/bit-git/tacapi_bot/raw/main/images/bot.gif)

# Prerequisites - Access to TAC APIs in Cisco API Console
This application requires access to the "Cisco Support API" provided at [https://apiconsole.cisco.com/](https://apiconsole.cisco.com/).  
Note, API access is granted by the SmartNet or PSS adminstrator.   

API documention: [https://developer.cisco.com/psirt/](https://developer.cisco.com/psirt/)

1. Ask SmartNet or PSS adminstrator to grant access to Cisco Support APIs. 
2. Register an app on the Cisco API Console and get client id and client secret.
3. Populate the creds.py file with the CLIENT_ID and CLIENT_SECRET

Example:
```
CLIENT_ID = "mxxgwertsps7ry9zsdkk7r3"
CLIENT_SECRET = "adqB3jegsvbYbJfcx27As5au"
```

# Prerequisites - Webex Teams Bot Account
Documentation: https://developer.webex.com/docs/bots

Create a free [Webex Teams](https://www.webex.com/products/teams/index.html) bot account.  [Register](https://www.webex.com/pricing/free-trial.html) here.

1. You'll need to start by adding your bot to the Webex Teams website.

    [https://developer.webex.com/my-apps](https://developer.webex.com/my-apps)

2. Click **Create a New App**

    ![add-app](https://github.com/bit-git/tacapi_bot/raw/main/images/createnewapp.png)

3. Click **Create a Bot**.

    ![create-bot](https://github.com/bit-git/tacapi_bot/raw/main/images/createnewbot.png)

4. Fill out all the details about your bot.  You'll need to set a name, username, icon (either upload one or choose a sample), and provide a description.

    ![add-bot](https://github.com/bit-git/tacapi_bot/raw/main/images/newbot.png)

5. Click **Add Bot**.

6. On the Congratulations screen, make sure to copy the *Bot's Access Token*, you will need this in creds.py.

    ![enter-details](https://github.com/bit-git/tacapi_bot/raw/main/images/botcongrats.png)

7. Populate the creds.py file with TEAMS_BOT_EMAIL and TEAMS_BOT_TOKEN

Example:
```
TEAMS_BOT_EMAIL = "tacbot@webex.bot"
TEAMS_BOT_TOKEN = "ABCABCABCAQtN2Q0OC00ZDQ3LWFlNTEtOTMzNTllYmU0MDE0MThkMDA1ZjEtNWZh_PF84_consumer"
```

# Prerequisites - ngrok

[ngrok](http://ngrok.com) will setup the tunnels for incoming message from Webex Teams.
If not ngrok, you can use your own public reachable HTTP(s) URL.

You can find installation instructions here: [https://ngrok.com/download](https://ngrok.com/download)

1. After you've installed `ngrok`, in another window start the service. </br>
   Specify the region `--region=eu` for Europe or `--region=us` for US.
   
    ```
    ngrok http 7001 --region=eu 
    ```
**Note:** There are limits for users who don't have a ngrok account: tunnels can only stay open for a fixed period of time and consume a limited amount of bandwidth.

You can always restart your tunnel to reset the limits, or you can remove the limits by signing up for a free account.</br> 
After you sign up, be sure to connect your account's authtoken to the ngrok client.

2. You should see a screen that looks like this:

    ```
    ngrok by @inconshreveable                                                                                                   (Ctrl+C to quit)

    Session Status                online
    Account                       my_ngrok_account@gmail.com (Plan: Free)
    Version                       2.3.35
    Region                        Europe (eu)
    Web Interface                 http://127.0.0.1:4040
    Forwarding                    http://63b24b1eb53c.eu.ngrok.io -> http://localhost:7001
    Forwarding                    https://63b24b1eb53c.eu.ngrok.io -> http://localhost:7001
    
    Connections                   ttl     opn     rt1     rt5     p50     p90
                                  0       0       0.00    0.00    0.00    0.00

    ```

# Installation
1. Git the code
	```
	git clone https://github.com/bit-git/tacapi_bot.git
	```

2. Create a virtualenv and install the webexteamsbot module

    ```
	cd tacapi_bot
    python3.6 -m venv .
    source bin/activate
    pip install webexteamsbot
    ```
	
# Usage
Launch the bot.

    ```
    python tacapi_bot.py
    ```

# Interacting with the bot

Search the bot on Webex Teams with the TEAMS_BOT_EMAIL. Interact direct or add in a group room.

In a group room you need to mention the bot - @tacbot

Example:

* @tacbot/sn2info FOC1234X0E6
* @tacbot/vul 16.12.4

You dont have to mention the bot in a direct room.

Example:

* /sn2info FOC1234X0E6
* /vul 16.12.4


# Credits
Hank Preston - https://github.com/hpreston/webexteamsbot

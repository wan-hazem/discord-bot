# Invite Links

- You want the bot on your server? [Click this link](https://discord.com/api/oauth2/authorize?client_id=713781013830041640&permissions=334622423&scope=bot)
- You have any ideas or issues with the bot? [Join the discord server](https://discord.gg/kGTku7H)

# About the bot
This is a pretty simple music bot writen in Pyhton 3.8.3. It includes:

| Category |                    Description                    |
|----------|---------------------------------------------------|
|Moderation|`!ban` `!unban` `!kick` `!mute`,  `!warn`, `!warns`|
|Music     |`!play` `!pause` `!skip` `!remove`                 |
|Chat      |`!help` `!poll` `!twitch`                          |
|Random    |`!toss` `!roll` `!meme` `!poke`                    |
|Weather   |`!weather`                                         |

# About the twitch command
This command allows you to search for streams by specifying a category and words.<br>
If you want to use the code, you'll have to:
- Get a twitch token by [following those steps](https://dev.twitch.tv/docs/authentication)
- Replace [this part](https://github.com/MrSpaar/discord-bot/blob/master/cogs/chat.py#L51-L54) to:
  ```python
  headers = {
      'Client-ID': "Client_ID",
      'Authorization': f"Bearer Twitch_Token",
  }
  ```
  
# About the weather command
This command will give you a city's instant and 5 days forecast.<br>
If you want to use the code, you'll have to:
- Create a Open>eatherMap [API key](https://home.openweathermap.org/api_keys)
- Replace [this part](https://github.com/MrSpaar/discord-bot/blob/master/cogs/weather.py#L18-L21) to:
  ```python
  def get_cast(city, forecast=False):
      key = "API_Key"
      if forecast:
          return rget(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&APPID={key}").json()
      data  = rget(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={key}").json()
  ```
    
# Libraries version

| Library | discord |discord.py|  PyNaCl |requests |  wheel  |youtube-dl |
|---------|---------|----------|---------|---------|---------|-----------|
| Version |  1.0.1  |   1.4.1  |  1.4.0  |  2.24.0 |  0.34.2 |2020.6.16.1|

# About the bot
This is a pretty simple music bot writen in Pyhton 3.8.3, that includes:

| Category |           Description            |
|----------|----------------------------------|
|Moderation|`!ban` `!unban` `!kick` `!mute`   |
|Music     |`!play` `!pause` `!skip` `!remove`|
|Chat      |`!help` `!poll` `!twitch`         |
|Random    |`!toss` `!roll` `!meme` `!poke`   |
|Weather   |`!weather`                        |

If you'd like to add my bot to your server, click [this link](https://discord.com/api/oauth2/authorize?client_id=713781013830041640&permissions=334622423&scope=bot).<br>If you have any issues or ideas, you can also join the bot's discord server [here](https://discord.gg/kGTku7H).

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
| Library  |  Version  |
|----------|-----------|
|discord   |1.0.1      |
|discord.py|1.4.1      |
|PyNaCl    |1.4.0      |
|requests  |2.24.0     |
|wheel     |0.34.2     |
|youtube-dl|2020.6.16.1|

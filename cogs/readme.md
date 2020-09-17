# Modifications à faire pour utiliser le code

- Commande `!annonce` :
  - Créer un [Token personnel Github](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
  - Remplacer [cette partie](https://github.com/MrSpaar/discord-bot/blob/master/cogs/admin.py#L111) par:
    ```python
    g = Github('GITHUB_TOKEN')
    ```
- Commande `!meteo` :
  - Créer une clé [API OpenWeatherMap](https://home.openweathermap.org/api_keys)
  - Remplacer [cette partie](https://github.com/MrSpaar/discord-bot/blob/master/cogs/weather.py#L18-L21) par:
    ```python
    def get_cast(city, forecast=False):
        key = "API_Key"
        if forecast:
            return rget(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&APPID={key}").json()
        data  = rget(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={key}").json()
    ```
- Commande `!twitch` :
  - Créer un Token Twitch en [suivant ces étapes](https://dev.twitch.tv/docs/authentication)
  - Remplacer [cette partie](https://github.com/MrSpaar/discord-bot/blob/master/cogs/chat.py#L51-L54) par:
    ```python
    headers = {
        'Client-ID': "Client_ID",
        'Authorization': f"Bearer Twitch_Token",
    }
    ```

# Liens d'invitation
Vous voulez ce bot sur votre serveur ? [Cliquez sur ce lien !](https://discord.com/api/oauth2/authorize?client_id=713781013830041640&permissions=334622423&scope=bot)<br>
Vous avez des idées, des recommendations ou des problèmes avec le bot ? [Rejoignez le discord !](https://discord.gg/H68KXcm)

# E - Wizard
C'est un bot *tout-en-un* écris en python (3.8.3) qui contient:

| Categorie |                        Description                         |
|----------|-------------------------------------------------------------|
|Moderation|`!ban` `!unban` `!kick` `!mute`  `!warn` `!warns` `!annonce` |
|Musique   |`!play` `!pause` `!skip` `!remove`                           |
|Chat      |`!help` `!sondage` `!twitch` `!profil`                       |
|Random    |`!pof` `!roll` `!meme` `!ping`                               |
|Météo     |`!météo`                                                     |

# Version des librairies
| Librarie | discord |discord.py|  PyNaCl |requests |  wheel  |youtube-dl |
|----------|---------|----------|---------|---------|---------|-----------|
|  Version |  1.0.1  |   1.4.1  |  1.4.0  |  2.24.0 |  0.34.2 |2020.6.16.1|

# A propos de la commande `!annonce`
Cette commande permet de faire des annonces.<br>
Si elle contient certains liens, un nouveau champ apparaîtra et contiendra :

|        Lien       |                   Contenu du champ               |
|-------------------|--------------------------------------------------|
|Repo Github        |Description / Topiques / Étoiles / Vues           |
|Invitations discord|Server name / Total Members / Total Online Members|

Pour réutiliser le code, il vous faut:
- Créer un [Token personnel Github](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
- Remplacer [cette partie](https://github.com/MrSpaar/discord-bot/blob/master/cogs/admin.py#L111) par:
  ```python
  g = Github('GITHUB_TOKEN')
  ```

# A propos de `!meteo`
Cette commande donne des prévisions météo sur 5 jours.<br>
Pour utiliser le code, il vous faut:
- Créer une clé [API OpenWeatherMap](https://home.openweathermap.org/api_keys)
- Remplacer [cette partie](https://github.com/MrSpaar/discord-bot/blob/master/cogs/weather.py#L18-L21) par:
  ```python
  def get_cast(city, forecast=False):
      key = "API_Key"
      if forecast:
          return rget(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&APPID={key}").json()
      data  = rget(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={key}").json()
  ```

# A propos de `!twitch`
Cette commande permet de rechercher des streams depuis twitch, à partir de mots-clés.<br>
Pour utiliser le code, il vous faut:
- Créer un Token Twitch en [suivant ces étapes](https://dev.twitch.tv/docs/authentication)
- Remplacer [cette partie](https://github.com/MrSpaar/discord-bot/blob/master/cogs/chat.py#L51-L54) par:
  ```python
  headers = {
      'Client-ID': "Client_ID",
      'Authorization': f"Bearer Twitch_Token",
  }
  ```

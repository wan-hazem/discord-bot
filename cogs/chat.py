from discord import Embed, Member, Color
from discord.ext import commands

from requests import get
from datetime import datetime
from sqlite3 import connect
from os import environ

class Chat(commands.Cog, name='Chat'):
    """
    Utilisable par tout le monde et rassemble toutes les commandes un peu random.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='!help [categorie]', description='Afficher ce message')
    async def help(self, ctx, category: str = None):
        embed = Embed(color=0x3498db)
        embed.title = '📋 Liste des catégories :' if not category else f'ℹ️ A propos de {category} :'
        await ctx.message.delete()
        if not category:
            for cat in self.bot.cogs:
                if cat in ['Test', 'Logs']:
                    pass
                else:
                    cog = self.bot.get_cog(cat)
                    embed.add_field(name=cat, value=f"{cog.description}\nÉcris `!help {cat}` pour plus d'infos.", inline=False)
        else:
            for cmd in self.bot.get_cog(category.capitalize()).get_commands():
                if cmd.hidden:
                    pass
                else:
                    embed.add_field(name=f"!{cmd.name}", value=f"{cmd.description} (`{cmd.brief}`)", inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief='!poll "[question]" [choix]', description='Créer un sondage (9 choix max)')
    async def poll(self, ctx, *items):
        question = items[0]
        answers = '\n'.join(items[1:])
        reactions = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
        embed = (Embed(title=':clipboard: Nouveau sondage', description=f"\> __{question}__", color=0x3498db)
                 .set_author(name=f'Par {ctx.author.display_name}', icon_url=ctx.author.avatar_url))

        await ctx.message.delete()
        for i in range(1, len(items)):
            embed.add_field(name=f"{reactions[i-1]} Option n°{i}", value=items[i], inline=False)
        message = await ctx.channel.send(embed=embed)

        for i in range(len(items[1:])):
            await message.add_reaction(reactions[i])

    @commands.command(brief='!twitch [jeu] [mots]', description='Rechercher des streams sur Twitch')
    async def twitch(self, ctx, game, *keys, streams=[]):
        headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': environ['TWITCH_CLIENT'],
            'Authorization': f"Bearer {environ['TWITCH_TOKEN']}",
        }
        category = get(f'https://api.twitch.tv/kraken/search/games?query={game}', headers=headers).json()['games'][0]
        embed = (Embed(title=f":desktop: Streams ({category['name']}):", color=0x3498db)
                 .set_thumbnail(url=category['box']['medium']))
        response = get(f"https://api.twitch.tv/helix/streams?game_id={category['_id']}", headers=headers).json()
        for stream in response['data']:
            if keys:
                for key in keys:
                    if key.lower() in stream['title'].lower() and not stream in streams:
                        streams.append(stream)
                        embed.add_field(name=f"{stream['user_name']}", value=f"[{stream['title']}](https://twitch.tv/{stream['user_name']})")
            else:
                embed.add_field(name=f"{stream['user_name']}", value=f"[{stream['title']}](https://twitch.tv/{stream['user_name']})")
        await ctx.send(embed=embed)

    @commands.command(brief='!profil [membre]', description="Afficher le profil d'un membre")
    async def profil(self, ctx, member: Member):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT WARNS FROM "{ctx.guild.id}" WHERE User_ID=?', (member.id,))
            entry = c.fetchone()
            warn_nb = len(entry.split('\n')) if entry else 0
        flags = [str(flag)[10:].replace('_', ' ').title() for flag in member.public_flags.all()]
        status = {'online': 'En ligne', 'offline': 'Hors ligne', 'invisible': 'Invisible', 'idle': 'Absent', 'dnd': 'Ne pas déranger'}
        embed = (Embed(color=0x1abc9c)
                 .add_field(name='📥 Membre depuis', value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
                 .add_field(name='⌨️ Pseudo', value=f'{member.name}#{member.discriminator}', inline=True)
                 .add_field(name='💡 Status', value=status[str(member.status)], inline=True)
                 .add_field(name='📝 Création du compte', value=member.created_at.strftime("%d/%m/%Y"), inline=True)
                 .add_field(name='🥇 Role principal', value=member.top_role.mention, inline=True)
                 .add_field(name='⚠️ Warns', value=f"{warn_nb} warns")
                 .add_field(name='🚩 Flags', value=', '.join(flags))
                 .add_field(name='Activité', value=member.activity.name if member.activity else 'Rien')
                 .set_author(name=f"Profil de {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                 .set_thumbnail(url=member.avatar_url))
        if member.premium_since:
            embed.add_field(name='📈 Booste depuis', value=member.premium_since.strftime("%d/%m/%Y"), inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Chat(bot))
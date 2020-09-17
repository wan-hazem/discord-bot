from discord import Embed, Member, Color
from discord.ext import commands
from discord.utils import get as dget

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

    @commands.command(hidden=True)
    async def rules(self, ctx):
        rules = {
            '👍 Règle n°1': "Respect mutuel ! Pour un chat sympa et bienveillant, pas d'insultes ou de méchancetés",
            '🗳️ Règle n°2': "C'est un serveur dédié à E - Wizard. Pas de sujets politiques, religieux et pas de racisme, de harcèlement ou de contenu offensif.",
            '🔕 Règle n°3': "Pas de spam ou de mentions abusives. Pour éviter d'avoir un chat qui ressembre à rien, évitez les abus.",
            '👦 Règle n°4': "Ayez un avatar et un pseudo approprié (family-friendly)",
            '🔒 Règle n°5': "Ne partagez pas vos informations personnelles ! Protégez votre intimité et celle des autres.",
            '💛 Règle n°6': "Utilisez votre bon sens. Ne faites pas aux autres ce que vous ne voudriez pas qu'on vous fasse.",
            '💬 Règle n°7': "Évitez la pub ! Vous pouvez partager vos projets dans #vos-projects.",
            '🙏 Règle n°8': "Pas de mandiage de role. C'est juste une perte de temps et ça ne marchera jamais.",
            '📑 Règle n°9': "Repectez les [Guidelines de la Communauté Discord](https://discord.com/guidelines) et les [Conditions d'utilisation](https://discord.com/terms).",
        }
        embed = Embed(title="📃 Règles du serveur:", color=0xa84300)
        embed.set_footer(text="Appuie sur ✔️ pour être vérifié !")
        for key, value in rules.items():
            embed.add_field(name=key, value=f"{value}\n", inline=False)
        await ctx.message.delete()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member
        if payload.emoji.name == '✅' and not member.bot:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id) 
            reaction = dget(message.reactions, emoji=payload.emoji.name)
            role = dget(member.guild.roles, name='Membre')
            if not role in member.roles:
                await member.add_roles(role)
            else:
                pass
            await reaction.remove(member)

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
        embed = Embed(title=f":desktop: Streams ({category['name']}):", color=0x3498db)
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
        flags = [str(flag)[10:].replace('_', ' ').capitalize() for flag in member.public_flags.all()]
        embed = (Embed(color=0x1abc9c)
                 .add_field(name='📥 Membre depuis', value=member.joined_at.strftime("%d %B, %Y"), inline=True)
                 .add_field(name='⌨️ Pseudo', value=f'{member.name}#{member.discriminator}', inline=True)
                 .add_field(name='💡 Status', value=str(member.status).capitalize(), inline=True)
                 .add_field(name='📝 Création du compte', value=member.created_at.strftime("%d %B, %Y"), inline=True)
                 .add_field(name='🥇 Role principal', value=member.top_role.name, inline=True)
                 .add_field(name='⚠️ Warns', value=f"{warn_nb} total warns")
                 .add_field(name='🚩 Flags', value=', '.join(flags))
                 .set_author(name=f"{ctx.author.display_name}'s profile", icon_url=ctx.author.avatar_url))
        if member.premium_since:
            embed.add_field(name='📈 Booste depuis', value=member.premium_since.strftime("%d %B, %Y"), inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Chat(bot))
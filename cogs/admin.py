from discord import Member, Embed, Status, Color, Role
from discord.ext import commands
from discord.utils import get

from os import environ
from asyncio import sleep
from sqlite3 import connect
from datetime import datetime
from re import findall
from github import Github

class Moderation(commands.Cog, name='Moderation'):
    """
    Commandes réservées aux admins et aux modos.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['purge'], brief='!clear [x]', description='Supprimer [x] messages')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, x: int):
        await ctx.channel.purge(limit=x+1)

    @commands.command(brief='!mute [membre] [durée] [raison]', description='Muter un membre')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: Member, time: str, *, reason: str = None):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute('SELECT Mute FROM setup WHERE Guild_ID=?', (ctx.guild.id,))
            role = get(ctx.guild.roles, id=c.fetchone()[0])
        units = {"s": [1, 'secondes'], "m": [60, 'minutes'], "h": [3600, 'heures']}
        duration = int(time[:-1]) * units[time[-1]][0]
        time = f"{time[:-1]} {units[time[-1]][1]}"
        embed = (Embed(description=f'Par : {ctx.author.mention}\nDurée : {time}.\nRaison : {reason}', color=0xe74c3c)
                 .set_author(name=f'{member} a été mute', icon_url=member.avatar_url))
        await ctx.send(embed=embed)
        await member.add_roles(role)
        await sleep(duration)
        await member.remove_roles(role)
        embed = Embed(color=0xe74c3c, description=f'{member.mention} a été unmute.')
        await ctx.send(embed=embed)

    @commands.command(brief='!kick [membre] [raison]', description='Kicker un membre')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason: str = None):
        embed = (Embed(description=f'Par : {ctx.author.mention}\nRaison : {reason}', color=0xe74c3c)
                 .set_author(name=f'{member} a été kick', icon_url=member.avatar_url))
        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(brief='!ban [membre] [raison]', description='Ban un membre')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason: str = None):
        embed = (Embed(description=f'Par : {ctx.author.mention}\nRaison : {reason}', color=0xe74c3c)
                 .set_author(name=f'{member} a été ban', icon_url=member.avatar_url))
        await member.ban(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(brief='!unban [membre] [raison]', description='Unban un membre')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: str, *, reason: str = None):
        ban_list = await ctx.guild.bans()
        if not ban_list:
            embed = Embed(title="Oups ! Quelque chose s'est mal passé :", description="Aucuns membres bannis !", color=0xe74c3c)
            await ctx.send(embed=embed); return
        for entry in ban_list:
            if member.lower() in entry.user.name.lower():
                embed = (Embed(description=f'Par : {ctx.author.avatar_url}\nRaison : {reason}', color=0x2ecc71)
                 .set_author(name=f'{member} a été unban', icon_url=member.avatar_url))
                await ctx.guild.unban(entry.user, reason=reason)
                await ctx.send(embed=embed); return
        embed = Embed(title="Something went wrong:", description="No matching user!", color=0xe74c3c)
        await ctx.send(embed=embed); return

    @commands.command(brief='!warn [membre] [raison]', description='Avertir un membre')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: Member, *, reason: str):
        now = datetime.now().strftime('%d/%m/%Y@%H:%M')
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT WARNS FROM "{ctx.guild.id}" WHERE User_ID=?', (member.id,))
            entry = c.fetchone()
            warns = (''.join(entry) if entry else '') + f'{now} - {reason}\n'
            if entry is None:
                c.execute(f'INSERT INTO "{ctx.guild.id}" (User_ID, Warns) VALUES (?, ?)', (member.id, warns))
            else:
                c.execute(f'UPDATE "{ctx.guild.id}" SET Warns=? WHERE User_ID=?', (warns, member.id))
            conn.commit()
        
        embed = (Embed(description=f'Par : {ctx.author.mention}\nRaison : {reason}', color=0xe74c3c)
                 .set_author(name=f'{member} a été warn', icon_url=member.avatar_url))
        await ctx.send(embed=embed)

    @commands.command(brief='!warns [membre]', description="Regarder les warns d'un membre")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: Member):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT WARNS FROM "{ctx.guild.id}" WHERE User_ID=?', (member.id,))
            warns = ''.join(c.fetchone())
        embed = Embed(color=0xe74c3c)
        for warn in warns.split('\n')[:-1]:
            date, reason = warn.split(' - ')
            embed.add_field(name=f"🚨 {date.replace('@', ' - ')}", value=f'{reason}', inline=False)
        embed.set_author(name=f"Warns de {member.display_name}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief='!annonce [texte]', description='Faire une annonce')
    @commands.has_permissions(manage_messages=True)
    async def annonce(self, ctx, *, text):
        embed = (Embed(title='Nouvelle annonce !', description=text, timestamp=datetime.now(), color=0xf1c40f)
                 .set_author(name=f'By {ctx.author.display_name}', icon_url=ctx.author.avatar_url))

        URL = findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)[0]
        if URL and 'github.com' in URL:
            name = URL[19:]
            g = Github(environ['GITHUB_TOKEN'])
            repo = g.get_repo(name)
            desc = f"*Description:* {repo.description}\n\
                    *Tags:* {' '.join([f'`{topic}`' for topic in repo.get_topics()])}\n\
                    *Statistiques:* {repo.stargazers_count} stars and {repo.get_views_traffic()['count']} views"
            embed.add_field(name=f'A propos de {name}', value=desc)
            embed.set_thumbnail(url=repo.owner.avatar_url)
        elif URL and 'discord.gg' in URL:
            invite = await self.bot.fetch_invite(URL)
            guild = invite.guild
            online = len([member for member in guild.members if member.status in [Status.online, Status.idle]])
            embed.add_field(name=f'A propos de {guild.name}', value=f'Rejoindre le serveur: {invite.url}\n🟢 {online} en ligne 🟤 {guild.member_count} membres', inline=False)
            embed.set_thumbnail(url=guild.icon_url)
        else:
            pass

        await ctx.message.delete()
        await ctx.send('@here', embed=embed)

    @commands.command(brief='!setup [verif/mute] [@role]', description='Définir un role pour les membres vérifiés ou mute')
    async def role(self, ctx, rtype: str, role: Role):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM setup WHERE Guild_ID=?', (ctx.guild.id,))
            guild = c.fetchone()
            if guild is None:
                c.execute(f'INSERT INTO setup (Guild_ID, {rtype.capitalize()}) VALUES (?, ?)', (ctx.guild.id, role.id))
            else:
                c.execute(f'UPDATE setup SET {rtype.capitalize()}=? WHERE Guild_ID=?', (role.id, ctx.guild.id))
            conn.commit()
        embed = (Embed(description=f'{ctx.author.mention} a défini {role.mention} pour "{rtype}"', color=0xa84300)
                 .set_author(name=f'{ctx.author} a modifié le role pour "{rtype}"', icon_url=ctx.author.avatar_url))
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def regles(self, ctx):
        rules = {
            '👍 Règle n°1': "Respect mutuel ! Pour un chat sympa et bienveillant, pas d'insultes ou de méchancetés",
            '🗳️ Règle n°2': "C'est un serveur dédié à @E - Wizard#3217. Pas de sujets politiques, religieux et pas de racisme, de harcèlement ou de contenu offensif.",
            '🔕 Règle n°3': "Pas de spam ou de mentions abusives. Pour éviter d'avoir un chat qui ressembre à rien, évitez les abus.",
            '👦 Règle n°4': "Ayez un avatar et un pseudo approprié (family-friendly)",
            '🔒 Règle n°5': "Ne partagez pas vos informations personnelles ! Protégez votre intimité et celle des autres.",
            '💛 Règle n°6': "Utilisez votre bon sens. Ne faites pas aux autres ce que vous ne voudriez pas qu'on vous fasse.",
            '💬 Règle n°7': "Évitez la pub ! Vous pouvez partager vos projets dans #vos-projects.",
            '🙏 Règle n°8': "Pas de mandiage de role. C'est juste une perte de temps et ça ne marchera jamais.",
            '📑 Règle n°9': "Repectez les [Guidelines de la Communauté Discord](https://discord.com/guidelines) et les [Conditions d'utilisation](https://discord.com/terms).",
        }
        embed = Embed(title="📃 Règles du serveur:", description='Appuie sur ✅ après avoir lu les règles :',color=0xa84300)
        for key, value in rules.items():
            embed.add_field(name=key, value=f"{value}\n", inline=False)
        await ctx.message.delete()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute('SELECT Verif FROM setup WHERE Guild_ID=?', (member.guild.id,))
            role = get(member.guild.roles, id=c.fetchone()[0])
        if payload.emoji.name == '✅' and not member.bot:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id) 
            reaction = get(message.reactions, emoji=payload.emoji.name)
            if not role in member.roles:
                await member.add_roles(role)
            await reaction.remove(member)


def setup(bot):
    bot.add_cog(Moderation(bot))
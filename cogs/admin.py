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


def setup(bot):
    bot.add_cog(Moderation(bot))
from discord import Member, Embed, Status, Color
from discord.ext import commands

from os import environ
from asyncio import sleep
from sqlite3 import connect
from datetime import datetime
from re import findall
from github import Github

class Moderation(commands.Cog, name='Moderation'):
    """
    Can only be used by moderators and admins.
    """
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def mute_handler(ctx, member, messages=False):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member, send_messages=messages)

    @commands.command(aliases=['purge'], brief='!clear [x]', description='Delete the [x] previous messages')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, x: int):
        await ctx.channel.purge(limit=x+1)

    @commands.command(brief='!mute [member] [duration] [reason]', description='Mute a member for the specified duration')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: Member, time: str, *, reason: str = None):
        units = {"s": [1, 'seconds'], "m": [60, 'minutes'], "h": [3600, 'hours']}
        duration = int(time[:-1]) * units[time[-1]][0]
        time = f"{time[:-1]} {units[time[-1]][1]}"
        await self.mute_handler(ctx, member)
        embed = Embed(title=":mute: User muted", description=f'{ctx.author.mention} muted **{member}** for {time}.\nReason: {reason}', color=0xe74c3c)
        await ctx.send(embed=embed)
        await sleep(duration)
        await self.mute_handler(ctx, member, True)
        embed = Embed(color=0xe74c3c, description=f'{member.mention} has been unmuted.')
        await ctx.send(embed=embed)

    @commands.command(brief='!kick [member] [reason]', description='Kick a member from the server')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason: str = None):
        embed = Embed(title="User kicked", description=f'{ctx.author.mention} kicked **{member}**.\nReason: {reason}', color=0xe74c3c)
        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(brief='!ban [member] [reason]', description='Ban a member from the server')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason: str = None):
        embed = Embed(title=":man_judge: User banned", description=f'{ctx.author.mention} banned **{member}**.\nReason: {reason}', color=0xe74c3c)
        await member.ban(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(brief='!unban [member] [reason]', description='Unban a member from the server')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: str, *, reason: str = None):
        ban_list = await ctx.guild.bans()
        if not ban_list:
            embed = Embed(title="Something went wrong:", description="No banned users!", color=0xe74c3c)
            await ctx.send(embed=embed); return
        for entry in ban_list:
            if member.lower() in entry.user.name.lower():
                embed = Embed(title=":man_judge: User unbanned", description=f'{ctx.author.mention} unbanned **{entry.user.mention}**.\nReason: {reason}', color=0xe74c3c)
                await ctx.guild.unban(entry.user, reason=reason)
                await ctx.send(embed=embed); return
        embed = Embed(title="Something went wrong:", description="No matching user!", color=0xe74c3c)
        await ctx.send(embed=embed); return

    @commands.command(brief='!warn [member] [reason]', description='Warn a member')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: Member, *, reason: str):
        now = datetime.now().strftime('%d/%m/%Y - %H:%M')
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT * FROM "{ctx.guild.id}" WHERE User_ID=?', (member.id,))
            entry = c.fetchone()
            if entry is None:
                warns = f"[1] {now}\n{reason}\n\n"
                c.execute(f'INSERT INTO "{ctx.guild.id}" (User_ID, Warns) VALUES (?, ?)', (member.id, warns))
            else:
                warn_nb, warns = len(list(entry)[1].split('\n\n')),  list(entry)[1]
                warns = f"{warns}[{warn_nb}] {now}\n{reason}\n\n"
                c.execute(f'UPDATE "{ctx.guild.id}" SET Warns=? WHERE User_ID=?', (warns, member.id))
            conn.commit()
        embed = Embed(title='⚠️ User warned', description=f'{ctx.author.mention} warned {member.mention}\n**Reason:** {reason}', color=0xe74c3c)
        await ctx.send(embed=embed)

    @commands.command(brief='!warns [member]', description="Get a member's warn list")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: Member):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT * FROM "{ctx.guild.id}" WHERE User_ID=?', (member.id,))
            user_id, warns = c.fetchone()
        embed = Embed(title=f"Warn list", description=member.mention, color=0xe74c3c)
        for warn in warns.split('\n\n')[:-1]:
            date, reason = warn.split('\n')
            embed.add_field(name=date, value=reason, inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief='!announce [text]', description='Make an announcement')
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, *, text):
        embed = (Embed(title='New announcement !', description=text, timestamp=datetime.now(), color=0xf1c40f)
                 .set_author(name=f'By {ctx.author.display_name}', icon_url=ctx.author.avatar_url))

        URL = findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)[0]
        if URL and 'github.com' in URL:
            name = URL[19:]
            g = Github(environ['GITHUB_TOKEN'])
            repo = g.get_repo(name)
            desc = f"*Description:* {repo.description}\n\
                    *Tags:* {' '.join([f'`{topic}`' for topic in repo.get_topics()])}\n\
                    *Statistics:* {repo.stargazers_count} stars and {repo.get_views_traffic()['count']} views"
            embed.add_field(name=f'About {name}', value=desc)
            embed.set_thumbnail(url=repo.owner.avatar_url)
        elif URL and 'discord.gg' in URL:
            invite = await self.bot.fetch_invite(URL)
            guild = invite.guild
            online = len([member for member in guild.members if member.status in [Status.online, Status.idle]])
            embed.add_field(name=f'About {guild.name}', value=f'Join here: {invite.url}\n🟢 {online} online 🟤 {guild.member_count} members', inline=False)
            embed.set_thumbnail(url=guild.icon_url)
        else:
            pass

        await ctx.message.delete()
        await ctx.send('@here', embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
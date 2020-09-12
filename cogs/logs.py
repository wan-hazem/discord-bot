from discord import Embed, Colour
from discord.ext import commands
from discord import AuditLogAction
from discord.utils import get

from datetime import datetime, timezone
from sqlite3 import connect

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_data(guild_id):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute("SELECT State FROM logs WHERE ID=?", (guild_id,))
            return int(c.fetchone()[0])

    @staticmethod
    def check_logs(guild, logs=False):
        state = Logs.get_data(guild.id)
        channel = get(guild.text_channels, name='logs')
        return False if ((not state or channel is None) and not logs) else True

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def logs(self, ctx):
        await ctx.message.delete()
        state = Logs.get_data(ctx.guild.id)
        with connect('data.db') as conn:
            c = conn.cursor()
            if state is None:
                c.execute("INSERT INTO logs(ID, State) VALUES(?, ?)", (ctx.guild.id, 1))
            elif state:
                c.execute("UPDATE logs SET State=? WHERE ID=?", (0, ctx.guild.id))
            else:
                c.execute("UPDATE logs SET State=? WHERE ID=?", (1, ctx.guild.id))
            conn.commit()
            state = 'disabled' if state else 'enabled'
            await ctx.send(f"Logs {state}", delete_after=5.0)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        param = error.param.name if isinstance(error, commands.MissingRequiredArgument) else ''
        perms = ', '.join(error.missing_perms) if isinstance(error, commands.BotMissingPermissions) else ''
        invoke_errors = {
            'index': "Index error!",
            'is_playing': "I'm not connected to any channel!",
            'unpack': "User has no warns !",
            'channel': "You're not connected to any channel!",
            'Missing Permissions': "I'm not allowed to do this!",
            'ValueError': 'Wrong arguments!',
            'KeyError': 'Wrong arguments!'
        }
        errors = {
            "<class 'discord.ext.commands.errors.MissingRequiredArgument'>": f'You forgot an argument: {param}',
            "<class 'discord.ext.commands.errors.CommandNotFound'>": 'Command not found!',
            "<class 'discord.ext.commands.errors.MissingPermissions'>": "You can't use this command!",
            "<class 'discord.ext.commands.errors.BotMissingPermissions'>": f'I need the following perms to do this: {perms} !',
            "<class 'discord.ext.commands.errors.BadArgument'>": 'You must input an integer!' if 'int' in str(error) else "Membre introuvable !",
            "<class 'discord.ext.commands.errors.CommandInvokeError'>": ''.join([value for key, value in invoke_errors.items() if key in str(error)]),
        }
        clean_error = errors[str(type(error))]
        if not clean_error:
            raise error
        embed = Embed(title="❌ Something went wrong:", description=clean_error, color=0xe74c3c)
        await ctx.message.delete()
        await ctx.send(embed=embed, delete_after=5.0)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        cmd = ctx.command.name
        state = Logs.get_data(ctx.guild.id)
        if not Logs.check_logs(ctx.guild, True if cmd=='logs' else False):
            return

        channel = get(ctx.guild.text_channels, name='logs')
        state = 'enabled' if state else 'disabled'
        
        cmd_args = ctx.message.content[len(cmd)+1:].split()
        if len(cmd_args)<2:
            cmd_args += ['', '']
        cmd_list = {
            'warn': {'title': ':warning: User warned', 'desc':f"{ctx.author.mention} warned {cmd_args[0]}\n**Reason:** {' '.join(cmd_args[1:])}", 'color': 0xe67e22},
            'mute': {'title': ':mute: User muted', 'desc': f"{ctx.author.mention} muted {cmd_args[0]}\n**Duration**: {cmd_args[1]}\n**Reason:** {' '.join(cmd_args[2:])}", 'color': 0xe74c3c},
            'clear': {'title': ':wastebasket:  Messages deleted', 'desc': f"{ctx.author.mention} deleted {cmd_args[0]} messages.", 'color': 0x1f8b4c},
            'poll': {'title': ':clipboard: Poll created', 'desc': f"Question: *{cmd_args[0]}*\nChoices: *{' / '.join(cmd_args[1:])}*\nBy {ctx.author.mention}",'color': 0x7289da},
            'logs': {'title': f':printer: Logs {state}', 'desc': f'{ctx.author.mention} {state} logs', 'color': 0x11806a},
        }

        if not cmd in cmd_list.keys():
            return

        embed = Embed(title=cmd_list[cmd]['title'], description=cmd_list[cmd]['desc'], color=cmd_list[cmd]['color'], timestamp=datetime.now())
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not Logs.check_logs(member.guild):
            return

        entry = await member.guild.audit_logs(limit=1).flatten()
        channel = get(member.guild.text_channels, name='logs')

        if entry[0].action == AuditLogAction.ban:
            embed = Embed(title=':man_judge: User banned', description=f"{entry[0].user.mention} banned {entry[0].target.mention}\n**Reason:** {entry[0].reason}", color=0xe74c3c, timestamp=datetime.now())
        elif entry[0].action == AuditLogAction.kick:
            embed = Embed(title=':man_judge: User kicked', description=f"{entry[0].user.mention} kicked {entry[0].target.mention}\n**Reason:** {entry[0].reason}", color=0xe74c3c, timestamp=datetime.now())
        else:
            embed = Embed(description=f'**:outbox_tray: {member.mention} left the server**', color=0xe74c3c, timestamp=datetime.now())
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if not Logs.check_logs(guild):
            return

        entry = await guild.audit_logs(limit=1).flatten()
        channel = get(guild.text_channels, name='logs')
        embed = Embed(title=':man_judge: User unbanned', description=f"{entry[0].user.mention} unbanned {entry[0].target}\n**Reason:** {entry[0].reason}", color=0xc27c0e, timestamp=datetime.now())
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not Logs.check_logs(member.guild):
            return

        channel = get(member.guild.text_channels, name='logs')
        embed = Embed(description=f'**:inbox_tray: {member.mention} joined the server**', color=0x2ecc71, timestamp=datetime.now())
        await channel.send(embed=embed)

        embed = Embed(title=":inbox_tray: New member !", description=f'{member.mention} joined the server', color=0x2ecc71, timestamp=datetime.now())
        embed.set_image(url=member.avatar_url)
        await member.guild.system_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not Logs.check_logs(before.guild):
            return

        entry = await after.guild.audit_logs(limit=1).flatten()
        channel = get(before.guild.text_channels, name='logs')
        embed = Embed(title=":notepad_spiral: Member modification", description=f'{entry[0].user.mention} changed {before.mention}', color=0x99aab5, timestamp=datetime.now())

        if before.display_name != after.display_name:
            embed.add_field(name="Nickname:", value=f"{before.display_name} → {after.display_name}")
        elif before.roles != after.roles:
            new_roles = [role.name for role in after.roles if role not in before.roles]
            removed_roles = [role.name for role in before.roles if role not in after.roles]
            new_roles = "New roles: "+("".join(new_roles) if new_roles else "None")
            removed_roles = "Removed roles: "+("".join(removed_roles) if removed_roles else "None")
            embed.add_field(name="Roles:", value=f"{new_roles}\n{removed_roles}")
        else:
            return
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = self.bot.fetch_channel(747480897426817095)
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO logs (ID, State) VALUES (?, ?)", (guild.id, 0))
            c.execute(f'CREATE TABLE IF NOT EXISTS "{guild.id}" (User_ID INTEGER, Warns TEXT)')
            conn.commit()
        embed = Embed(title='📥 New server', description=f"I joined this server: **{guild.name}**")
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))
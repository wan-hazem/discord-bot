from discord import Embed, Colour
from discord.ext import commands
from discord.utils import get

from datetime import datetime, timezone
from sqlite3 import connect

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def create_embed(title=None, description=None , color=None, timestamp=None):
        embed = Embed(
            title=title,
            description=description,
            color=color,
            timestamp=timestamp
        )
        return embed

    @staticmethod
    def get_data(guild_id):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM guilds WHERE ID=?", (guild_id,))
            return c.fetchone()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def logs(self, ctx):
        await ctx.message.delete()
        state = Logs.get_data(ctx.guild.id)
        with connect('data.db') as conn:
            c = conn.cursor()
            if state == None:
                c.execute("INSERT INTO guilds(ID, State) VALUES(?, ?)", (ctx.guild.id, 1))
            elif state == (ctx.guild.id, 0):
                c.execute("UPDATE guilds SET State=? WHERE ID=?", (1, ctx.guild.id))
            else:
                c.execute("UPDATE guilds SET State=? WHERE ID=?", (0, ctx.guild.id))
            conn.commit()
            state = 'disabled' if state==(ctx.guild.id, 0) else 'enabled'
            await ctx.send(f"Logs {state}", delete_after=5.0)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            msg = f'You forgot arguments: {error.param.name}'
        elif isinstance(error, commands.CommandNotFound):
            msg = 'Command not found!'
        elif isinstance(error, commands.MissingPermissions):
            msg = "You can't use this command!"
        elif isinstance(error, commands.BotMissingPermissions):
            perms = ', '.join(error.missing_perms)
            msg = f'I need the following perms to do this: {perms} !'
        elif isinstance(error, commands.BadArgument):
            if 'int' in str(error):
                msg = 'You must input an integer!'
            elif 'Member' in str(error):
                msg = "Membre introuvable !"
        elif isinstance(error, commands.CommandInvokeError):
            if 'index' in str(error):
                msg = "Index error!"
            elif 'NoneType' in str(error):
                msg = "I'm not connected to any channel!" if 'is_playing' in str(error) else "You're not connected to any channel!"
            elif ('ValueError' or 'KeyError') in str(error):
                msg = 'Wrong arguments!'
            elif 'Missing Permissions' in str(error):
                msg = "I'm not allowed to do this!"
            else:
                raise error
        else:
            raise error

        embed = Embed(title="❌ Something went wrong:", description=msg, color=0xe74c3c)
        await ctx.message.delete()
        await ctx.send(embed=embed, delete_after=5.0)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        state = Logs.get_data(ctx.guild.id)
        if state == None or (ctx.command.name!='logs' and state==(ctx.guild.id, 0)):
            return
        cmd = ctx.command.name
        cmd_args = ctx.message.content[len(cmd)+1:].split()
        cmd_list = {
            "ban": {"word": "banned", "color": 0xe74c3c},
            "unban": {"word": "unbanned", "color": 0xc27c0e},
            "kick": {"word": "kicked", "color": 0xe74c3c},
            "mute": {"word": "muted", "color": 0xe74c3c},
            "clear": {"word": "deleted", "color": 0x1f8b4c},
            "poll": {"color": 0x7289da},
            "logs": {"color": 0x11806a},
        }
        channel = get(ctx.guild.text_channels, name='logs')
        if not cmd in cmd_list.keys():
            return
        if cmd in ['ban', 'unban', 'kick']:
            title = f":man_judge: User {cmd_list[cmd]['word']}"
            description = f"{ctx.author.mention} {cmd_list[cmd]['word']} {cmd_args[0]}\n**Reason:** {' '.join(cmd_args[1:])}"
        elif cmd == 'mute':
            title = f":mute: User {cmd_list[cmd]['word']}"
            description = f"{ctx.author.mention} {cmd_list[cmd]['word']} {cmd_args[0]}\n**Duration**: {cmd_args[1]}\n**Reason:** {' '.join(cmd_args[2:])}"
        elif cmd == 'clear':
            title = f":wastebasket:  Messages {cmd_list[cmd]['word']:}"
            description = f"{ctx.author.mention} {cmd_list[cmd]['word']} {cmd_args[0]} messages."
        elif cmd == 'poll':
            title = ':clipboard: Poll created:'
            description = f"Question: *{cmd_args[0]}*\nChoices: *{' / '.join(cmd_args[1:])}*\nBy {ctx.author.mention}"
        elif cmd == 'logs':
            state = 'enabled' if state==(ctx.guild.id, 1) else 'disabled'
            title = f':printer: Logs {state}:'
            description = f'{ctx.author.mention} {state.strip("s")} logs'
        else:
            return
        embed = Logs.create_embed(title, description, cmd_list[cmd]['color'], datetime.now())
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        state = Logs.get_data(member.guild.id)
        if state == None or state == (member.guild.id, 0): return
        channel = get(member.guild.text_channels, name='logs')
        embed = Logs.create_embed(None, f'**:outbox_tray: {member.mention} left the server**', 0xe74c3c, datetime.now())
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        state = Logs.get_data(member.guild.id)
        if state == None or state == (member.guild.id, 0): return
        channel = get(member.guild.text_channels, name='logs')
        embed = Logs.create_embed(None, f'**:inbox_tray: {member.mention} joined the server**', 0x2ecc71, datetime.now())
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        state = Logs.get_data(before.guild.id)
        if state == None or state == (before.guild.id, 0): return
        channel = get(before.guild.text_channels, name='logs')
        embed = Logs.create_embed(":notepad_spiral: Member modification:", before.mention, 0x99aab5, datetime.now())
        if before.display_name != after.display_name :
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
        channel = self.bot.fetch_channel(730780408773345280)
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO guilds (ID, State) VALUES (?, ?)", (guild.id, 0))
            conn.commit()
        embed = Embed(title='📥 Joined a server', description=f"I joined this server: **{guild.name}**")
        await channel.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Logs(bot))
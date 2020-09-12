from discord import Embed, Member, Color
from discord.ext import commands
from discord.utils import get as dget

from requests import get
from datetime import datetime
from sqlite3 import connect
from os import environ

class Chat(commands.Cog, name='Chat'):
    """
    Can be used by everyone and gathers every non specific commands.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='!help [category]', description='Show this message')
    async def help(self, ctx, category: str = None):
        embed = Embed(color=0x3498db)
        embed.title = '📋 Category list:' if not category else f'ℹ️ About the {category} category:'
        await ctx.message.delete()
        if not category:
            for cat in self.bot.cogs:
                if cat in ['Test', 'Logs']:
                    pass
                else:
                    cog = self.bot.get_cog(cat)
                    embed.add_field(name=cat, value=f"{cog.description}\nType `!help {cat}` for more informations.", inline=False)
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
            '👍 Rule n°1': "Respect eachother! For a nice and kind chat, don't swear or be mean.",
            '🗳️ Rule n°2': "This server is dedicated to Hazard Wizard. That means no political or religious topics, racism, harassment or offensive content.",
            '🔕 Rule n°3': "Don't spam and don't abuse mentions. We want clear and understandable chats, not a weird mess.",
            '👦 Rule n°4': "Use an appropriate nickname and avatar. Keep it family-friendly.",
            '🔒 Rule n°5': "Don't share personnal informations! Protect your privacy and other's privacy.",
            '💛 Rule n°6': "Use your common sense. Do not do to others what you would not done to you.",
            '💬 Rule n°7': "Self-promotions is forbidden! You can only share your projects in #your-projects.",
            '🙏 Rule n°8': "Don't beg for roles/permissions. It's just annoying and you'll never get roles by begging.",
            '📑 Rule n°9': "Follow [Discord Community Guidelines](https://discord.com/guidelines) and [Terms Of Service](https://discord.com/terms).",
        }
        embed = Embed(title="📃 Server's rules:", color=0xa84300)
        embed.set_footer(text="Click ✔️ to access the server")
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
            role = dget(member.guild.roles, name='Member')
            if not role in member.roles:
                await member.add_roles(role)
            else:
                pass
            await reaction.remove(member)

    @commands.command(brief='!poll "[question]" [choices]', description='Create a poll (9 maximum choices)')
    async def poll(self, ctx, *items):
        question = items[0]
        answers = '\n'.join(items[1:])
        reactions = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
        embed = (Embed(title=':clipboard: New poll', description=f"\> __{question}__", color=0x3498db)
                 .set_author(name=f'By {ctx.author.display_name}', icon_url=ctx.author.avatar_url))

        await ctx.message.delete()
        for i in range(1, len(items)):
            embed.add_field(name=f"{reactions[i-1]} Option n°{i}", value=items[i], inline=False)
        message = await ctx.channel.send(embed=embed)

        for i in range(len(items[1:])):
            await message.add_reaction(reactions[i])

    @commands.command(brief='!twitch [game] [words]', description='Search for streams on twitch')
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

    @commands.command(brief='!profile [member]', description="Display member's profile")
    async def profile(self, ctx, member: Member):
        with connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT * FROM "{ctx.guild.id}" WHERE User_ID=?', (member.id,))
            user_id, warns = c.fetchone()
        flags = [str(flag)[10:].replace('_', ' ').capitalize() for flag in member.public_flags.all()]
        embed = (Embed(color=0x1abc9c)
                 .add_field(name='📥 Member Since', value=member.joined_at.strftime("%d %B, %Y"), inline=True)
                 .add_field(name='⌨️ Nickname', value=f'{member.name}#{member.discriminator}', inline=True)
                 .add_field(name='💡 Status', value=str(member.status).capitalize(), inline=True)
                 .add_field(name='📝 Account Creation', value=member.created_at.strftime("%d %B, %Y"), inline=True)
                 .add_field(name='🥇 Top role', value=member.top_role.name, inline=True)
                 .add_field(name='⚠️ Warns', value='')
                 .add_field(name='🚩 Flags', value=', '.join(flags))
                 .set_author(name=f"{ctx.author.display_name}'s profile", icon_url=ctx.author.avatar_url))
        if member.premium_since:
            embed.add_field(name='📈 Boosting since', value=member.premium_since.strftime("%d %B, %Y"), inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Chat(bot))
from discord import Embed
from discord.ext import commands

from requests import get, post
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

    @commands.command(brief='!poll "[question]" [choices]', description='Create a poll (9 maximum choices)')
    async def poll(self, ctx, *items):
        question = items[0]
        answers = '\n'.join(items[1:])
        embed = Embed(title='New poll:', description=f":grey_question: __{question}__", color=0x3498db)
        await ctx.message.delete()
        for i in range(1, len(items)):
            embed.add_field(name=f"Option n°{i}", value=items[i], inline=False)
        embed.set_footer(text=f"Asked by: {ctx.author}")
        message = await ctx.channel.send(embed=embed)
        reactions = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']

        for i in range(len(items[1:])):
            await message.add_reaction(reactions[i])

    @commands.command(brief='!twitch [game] [words]', description='Search for streams on twitch')
    async def twitch(self, ctx, game, *keys, streams=[]):
        headers = {
            'Client-ID': environ['TWITCH_CLIENT'],
            'Authorization': f"Bearer {environ['TWITCH_TOKEN']}",
        }
        topgames = get(f"https://api.twitch.tv/helix/games/top?first=100", headers=headers).json()
        for category in topgames['data']:
            if game.lower() in category['name'].lower():
                embed = Embed(title=f":desktop: Streams ({category['name']}):", color=0x3498db)
                stream_nb = 100 if keys else 20
                response = get(f"https://api.twitch.tv/helix/streams?game_id={category['id']}&first={stream_nb}", headers=headers).json()
                for stream in response['data']:
                    if keys:
                        for key in keys:
                            if key.lower() in stream['title'].lower() and not stream in streams:
                                streams.append(stream)
                                embed.add_field(name=f"{stream['user_name']}", value=f"[{stream['title']}](https://twitch.tv/{stream['user_name']})")
                    else:
                        embed.add_field(name=f"{stream['user_name']}", value=f"[{stream['title']}](https://twitch.tv/{stream['user_name']})")
                await ctx.send(embed=embed)
                return
        embed = Embed(title=f"❌ Something went wrong:", description="No available streams", color=0xe74c3c)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Chat(bot))
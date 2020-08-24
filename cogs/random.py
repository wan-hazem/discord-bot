from discord import Embed
from discord.ext import commands
from discord.utils import get

from random import choice, randint
from requests import get as rget

class Random(commands.Cog, name='Random'):
    """
    Can be used by anyone, you'll find games and random related commands here.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='!toss [heads/tails]', description='Make a coin toss against the bot')
    async def toss(self, ctx, arg):
        if arg.lower() == 'heads' or arg.upper() == 'tails':
            piece = choice(['heads', 'tails'])
            if arg.lower() in piece:
                await ctx.send(f':white_check_mark: {piece}! You won.')
            else:
                await ctx.send(f':negative_squared_cross_mark:  {piece}! You lost.')
        else:
            await ctx.send('❌ You must input either "heads" or "tails"!')         

    @commands.command(brief='!poke [random/nickname]', description="Mention someone")
    async def poke(self, ctx, arg):
        members = [x for x in ctx.guild.members if not x.bot]
        if arg.lower() == 'random':
            await ctx.send(f'Hey {choice(members).mention} !')
        else:
            await ctx.send(f'Hey {arg.mention} !')

    @commands.command(aliases=['r'], brief='!roll [x]', description="Roll a [x] sided dice")
    async def roll(self, ctx, faces: int):
        number = randint(1, faces)
        await ctx.send(f'🎲 You rolled a {number} !')

    @commands.command(brief='!meme', description='Watch a random meme from reddit')
    async def meme(self, ctx):
        data = rget('https://meme-api.herokuapp.com/gimme').json()
        embed = (Embed(title=f":speech_balloon: r/{data['subreddit']} :", color=0x3498db)
                .set_image(url=data['url'])
                .set_footer(text=data['postLink']))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Random(bot))
from discord import Game
from discord.ext import commands
from os import environ

bot = commands.Bot(command_prefix=['!', '$'])
bot.remove_command('help')
initial_extensions = ['cogs.admin', 'cogs.music', 'cogs.chat', 'cogs.random', 'cogs.weather', 'cogs.logs']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'\nConnecté en tant que : {bot.user.name} - {bot.user.id}')
    await bot.change_presence(activity=Game(name='!help'))
    print(f'Le Bot est opérationnel !')

bot.run(environ['BOT_TOKEN'], bot=True, reconnect = True)
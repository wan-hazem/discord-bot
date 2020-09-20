from discord import Role, Embed, Color
from discord.ext import commands
from discord.utils import get

from sqlite3 import connect

class Setup(commands.Cog, name='Setup'):
    """
    Commandes de setup serveur réservées aux admins
    """
    def __init__(self, bot):
        self.bot = bot

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
    bot.add_cog(Setup(bot))
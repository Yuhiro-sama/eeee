import discord
from discord.ext import commands
import asyncio
import unidecode


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def nickname(self, ctx, member: discord.member,*, nick):
        await member.edit(nick=nick)
        await ctx.send("Succesfully changed")
    
    
    @commands.command(aliases=["dw"])
    @commands.has_guild_permissions(administrator=True)
    async def del_web(self, ctx, channel : discord.TextChannel=None):
        channel = channel or ctx.channel
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            await webhook.delete()
        await ctx.send("All webhoocks are succesfully deleted. ")
        
    @commands.command(
        name="kick",
        description="A command which kicks a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            return await ctx.send("Vous n'avez qu'a quitté au lieu de vouloir vous expulser !")
        
    
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(f"You can't do that. !")         
        
        await ctx.guild.kick(user=member, reason=reason)

        # Using our past episodes knowledge can we make the log channel dynamic?
        embed = discord.Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="ban",
        description="A command which bans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            return await ctx.send("Vous n'avez qu'a quitté au lieu de vouloir vous expulser !")
        
    
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(f"You can't do that. !")    
        await ctx.guild.ban(user=member, reason=reason)

        # Using our past episodes knowledge can we make the log channel dynamic?
        embed = discord.Embed(
            title=f"{ctx.author.name} banned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)
    @commands.command(aliases=['sban'], pass_context=True)
    async def softban(self, ctx, user:discord.Member, *, reason=""):
        """Bans and unbans a user (if you have the permission)."""
        if user:
            if user == ctx.author:
                return await ctx.send("Vous n'avez qu'a quitté au lieu de vouloir vous expulser !")
            if user.top_role >= ctx.author.top_role:
                return await ctx.send(f"You can't do that. !")   
            try:
                await user.ban(reason=reason)
                await ctx.guild.unban(user)
                return_msg = "Banned and unbanned user `{}`".format(user.mention)
                if reason:
                    return_msg += " for reason `{}`".format(reason)
                return_msg += "."
                await ctx.message.edit(return_msg)
            except discord.Forbidden:
                await ctx.message.edit('Could not softban user. Not enough permissions.')
        else:
            return await ctx.message.edit('Could not find user.')

    @commands.command(
        name="unban",
        description="A command which unbans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def unban(self, ctx, member, *, reason=None):
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)
        if reason is None:
            reason = "Non précisé"

        embed = discord.Embed(
            title=f"{ctx.author.name} unbanned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)
    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def banlist(self, ctx):
        banList = await ctx.guild.bans()
        banString = ""
        count = 0

        if len(banList) > 0:
            for ban in banList:
                user = ban.user
                reason = ban.reason
                if reason is None:
                    reason = "Non précisé"
                    

                count += 1
                banString += f"{count}: {user.name}#{user.discriminator}  |  {user.id}  |  {reason}\n"
                
            embed = discord.Embed(title="SERVER BANS", description=f"\n\n{banString}\n")
            await ctx.send(embed=embed)
        else:
            await ctx.send("There are no users currently banned from this server")
            
    @commands.command(description="Ban a user, even when not in the server.",
                      aliases=['shadowban', 'hban'])
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def hackban(self, ctx, user: int, *, reason: str=None):
        'Ban someone, even when not in the server.'

        await ctx.bot.http.ban(user, ctx.guild.id, 7, reason=f'[{str(ctx.author)}] {reason}' if reason else f'Hackban by {str(ctx.author)}')
        msg = await ctx.send(':ok_hand:')
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(description='Decancer a member.')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def decancer(self, ctx, member: discord.Member):
        '"Decancer" a member, or strip all the non-ASCII characters from their name. Useful to make your chat look good.'
        try:
            if ctx.author.permissions_in(ctx.channel).manage_nicknames:
                cancer = member.display_name
                decancer = unidecode.unidecode_expect_nonascii(cancer)
                # decancer = re.sub(r'\D\W', '', decancer)
                if len(decancer) > 32:
                    decancer = decancer[0:32 - 3] + "..."

                await member.edit(nick=decancer)
                await ctx.send(
                    f'Successfully decancered {cancer} to `{decancer}`.')

            else:
                cancer = member.display_name
                decancer = unidecode.unidecode_expect_nonascii(cancer)
                await ctx.send(
                    f'The decancered version of {cancer} is `{decancer}`.')
        except discord.Forbidden:
            await ctx.send(f"I don't have permission to decancer **{member}**")
    

    

def setup(bot):
    bot.add_cog(Moderation(bot))
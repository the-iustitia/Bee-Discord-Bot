import discord
from discord.ext import commands
from games import timecountry as tc


class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def time(self, ctx, country: str):
        await ctx.defer()

        name, tz, current = tc.get_time_by_country(country)

        if not name:
            return await ctx.followup.send("Country not found")

        if not tz:
            return await ctx.followup.send(f"{name}: timezone not found")

        embed = discord.Embed(
            title="Country Time",
            color=0x2b2d31
        )

        embed.add_field(name="Country", value=name, inline=False)
        embed.add_field(name="Time zone", value=tz, inline=False)
        embed.add_field(name="Current time", value=current, inline=False)

        await ctx.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(TimeCog(bot))
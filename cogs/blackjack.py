import discord
import asyncio
from games.blackjack import draw, calculate, dealer_play, get_result


class BlackjackView(discord.ui.View):
    def __init__(self, player, dealer):
        super().__init__(timeout=60)
        self.player = player
        self.dealer = dealer
        self.lock = False

    def embed(self, reveal=False):
        dealer_text = (
            str(self.dealer)
            if reveal
            else f"[{self.dealer[0]}, ❓]"
        )

        return discord.Embed(
            title="♠ Blackjack",
            description=f"""
🃏 Your hand: {self.player} ({calculate(self.player)})
🎴 Dealer: {dealer_text}
            """,
            color=0xffcc00
        )

    async def finish(self, interaction):
        dealer_play(self.dealer)
        result = get_result(self.player, self.dealer)

        embed = discord.Embed(
            title="♠ Blackjack Result",
            description=f"""
You: {self.player} = {calculate(self.player)}
Dealer: {self.dealer} = {calculate(self.dealer)}

Result: **{result.upper()}**
            """,
            color=0xffcc00
        )

        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, button, interaction: discord.Interaction):
        if self.lock:
            return

        self.lock = True

        self.player.append(draw())

        if calculate(self.player) > 21:
            await self.finish(interaction)
            return

        await interaction.response.edit_message(
            embed=self.embed(),
            view=self
        )

        await asyncio.sleep(0.5)
        self.lock = False

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, button, interaction: discord.Interaction):
        if self.lock:
            return

        self.lock = True
        await self.finish(interaction)


async def start_blackjack(ctx):
    player = [draw(), draw()]
    dealer = [draw(), draw()]

    view = BlackjackView(player, dealer)

    await ctx.respond(embed=view.embed(), view=view)
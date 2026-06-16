import discord
import asyncio
from games import rps as rps_game


CHOICES = ["rock", "paper", "scissors"]


EMOJI = {
    "rock": "🪨",
    "paper": "📄",
    "scissors": "✂️"
}


class RPSView(discord.ui.View):
    def __init__(self, p1, p2=None):
        super().__init__(timeout=60)

        self.p1 = p1
        self.p2 = p2
        self.vs_bot = p2 is None

        self.moves = {}
        self.lock = False

        for c in CHOICES:
            self.add_item(RPSButton(c))


    def done(self):
        if self.vs_bot:
            return self.p1.id in self.moves
        return len(self.moves) == 2


    def evaluate(self):
        p1_move = self.moves[self.p1.id]

        if self.vs_bot:
            bot = rps_game.bot_choice()
            res = rps_game.result(p1_move, bot)
            return p1_move, bot, res

        p2_move = self.moves[self.p2.id]
        res = rps_game.result(p1_move, p2_move)
        return p1_move, p2_move, res


class RPSButton(discord.ui.Button):
    def __init__(self, choice):
        super().__init__(
            label=choice,
            style=discord.ButtonStyle.secondary
        )
        self.choice = choice

    async def callback(self, interaction: discord.Interaction):
        view: RPSView = self.view

        if view.lock:
            return await interaction.response.defer()

        if view.vs_bot:
            if interaction.user.id != view.p1.id:
                return await interaction.response.send_message("Not your game")
        else:
            if interaction.user.id not in [view.p1.id, view.p2.id]:
                return await interaction.response.send_message("Not in game")

        if interaction.user.id in view.moves:
            return await interaction.response.send_message("Already picked")

        view.moves[interaction.user.id] = self.choice

        await interaction.response.defer()

        if not view.done():
            return

        view.lock = True
        await asyncio.sleep(0.5)

        p1_move, p2_move, res = view.evaluate()

        for c in view.children:
            c.disabled = True

        embed = discord.Embed(
            title="Rock Paper Scissors Result",
            color=0x2b2d31
        )

        embed.add_field(
            name=view.p1.display_name,
            value=f"{p1_move}",
            inline=True
        )

        if view.vs_bot:
            embed.add_field(
                name="Bot",
                value=f"{p2_move}",
                inline=True
            )
        else:
            embed.add_field(
                name=view.p2.display_name,
                value=f"{p2_move}",
                inline=True
            )

        if view.vs_bot:
            if res == "win":
                outcome = "You win"
            elif res == "lose":
                outcome = "You lose"
            else:
                outcome = "Draw"
        else:
            if res == "win":
                outcome = f"{view.p1.mention} wins"
            elif res == "lose":
                outcome = f"{view.p2.mention} wins"
            else:
                outcome = "Draw"

        embed.add_field(name="Result", value=outcome, inline=False)

        await interaction.message.edit(embed=embed, view=view)
        view.stop()

        if not view.done():
            return

        view.lock = True

        await asyncio.sleep(0.5)

        p1_move, p2_move, res = view.evaluate()

        if view.vs_bot:
            if res == "win":
                text = f"You win ({p1_move} vs {p2_move})"
            elif res == "lose":
                text = f"You lose ({p1_move} vs {p2_move})"
            else:
                text = f"Draw ({p1_move})"
        else:
            if res == "win":
                text = f"{view.p1.mention} wins"
            elif res == "lose":
                text = f"{view.p2.mention} wins"
            else:
                text = "Draw"

        for c in view.children:
            c.disabled = True

        await interaction.message.edit(content=text, view=view)
        view.stop()


async def start_rps(ctx, opponent=None):
    view = RPSView(ctx.author, opponent)

    mode = "Bot" if opponent is None else f"PvP vs {opponent}"

    await ctx.respond(
        content=f"RPS started ({mode})",
        view=view
    )
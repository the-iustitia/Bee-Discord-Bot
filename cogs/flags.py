import discord
import asyncio
from utils.economy import add
from games.flags import get_question


class FlagsView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30)

        self.user = user
        self.data = get_question()

        self.lock = False
        self.wins = 0
        self.total = 0

        self.message = None
        self.result_message = None

        self.history = []

        self._build()

    def _build(self):
        self.clear_items()

        for ans in self.data["answers"]:
            self.add_item(AnswerButton(ans))

        self.add_item(StopButton())

    def make_embed(self):
        e = discord.Embed(
            title="🌍 Guess the Flag",
            description="Choose the correct country",
            color=0x00ffcc
        )
        e.set_image(url=self.data["flag_url"])
        return e

    async def next_round(self):
        self.data = get_question()
        self.lock = False
        self._build()
        await self.message.edit(embed=self.make_embed(), view=self)

    async def finish(self, reason="timeout"):
        for c in self.children:
            c.disabled = True

        accuracy = (self.wins / self.total * 100) if self.total else 0

        history_text = ""
        for item in self.history[-10:]:
            history_text += f"{item['flag']} → {item['name']}\n"

        if not history_text:
            history_text = "None"

        embed = discord.Embed(
            title="📊 Flag Game Results",
            description=f"Player: {self.user.mention}",
            color=0xffcc00
        )

        embed.add_field(
            name="Stats",
            value=(
                f"Total answers: **{self.total}**\n"
                f"Wins: **{self.wins}**\n"
                f"Accuracy: **{accuracy:.1f}%**"
            ),
            inline=False
        )

        embed.add_field(
            name="Correct flags (last rounds)",
            value=history_text,
            inline=False
        )

        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )

        # ❗ ВАЖНО: не создаём новое сообщение
        await self.message.edit(embed=embed, view=None)

        self.stop()


class AnswerButton(discord.ui.Button):
    def __init__(self, answer):
        super().__init__(
            label=answer,
            style=discord.ButtonStyle.secondary
        )
        self.answer = answer

    async def callback(self, interaction: discord.Interaction):
        view: FlagsView = self.view

        if interaction.user != view.user:
            return await interaction.response.send_message("Not your game", ephemeral=True)

        if view.lock:
            return await interaction.response.defer()

        view.lock = True

        correct = view.data["correct"]
        flag_url = view.data["flag_url"]

        view.total += 1

        if self.answer == correct:
            self.style = discord.ButtonStyle.success
            view.wins += 1
            add(view.user.id, 5)
            result = "Correct +5"
        else:
            self.style = discord.ButtonStyle.danger
            add(view.user.id, -2)
            result = f"Wrong! It was **{correct}**"

        view.history.append({
            "flag": flag_url,
            "name": correct
        })

        for c in view.children:
            if isinstance(c, AnswerButton):
                c.disabled = True

        await interaction.response.edit_message(content=result, view=view)

        await asyncio.sleep(1)

        await view.next_round()


class StopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Stop",
            style=discord.ButtonStyle.red
        )

    async def callback(self, interaction: discord.Interaction):
        view: FlagsView = self.view

        if interaction.user != view.user:
            return await interaction.response.send_message("Not your game", ephemeral=True)

        await interaction.response.defer()
        await view.finish(reason="stopped by player")


async def start_flags(ctx):
    view = FlagsView(ctx.author)

    msg = await ctx.respond(embed=view.make_embed(), view=view)
    view.message = await msg.original_response()

    try:
        await asyncio.sleep(30)
        if not view.is_finished():
            await view.finish(reason="timeout")
    except:
        pass
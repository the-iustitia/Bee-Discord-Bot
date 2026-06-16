import discord
import asyncio
from utils.economy import add
from games.slots import roll, evaluate


class SlotsView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        self.cooldown = False

        for i in range(5):
            self.add_item(SlotCell(i))

        self.add_item(RollButton())


class SlotCell(discord.ui.Button):
    def __init__(self, index):
        super().__init__(
            label="⬜",
            style=discord.ButtonStyle.secondary,
            row=0,
            disabled=True
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class RollButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="ROLL",
            style=discord.ButtonStyle.success,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        view: SlotsView = self.view

        if interaction.user != view.user:
            return await interaction.response.send_message("Not your game", ephemeral=True)

        if view.cooldown:
            return

        view.cooldown = True
        self.disabled = True

        await interaction.response.defer()

        spin, _ = roll()
        result = evaluate(spin)

        for child in view.children:
            if isinstance(child, SlotCell):
                child.label = spin[child.index]

        if result == "win":
            add(view.user.id, 100)
            status = "WIN +100"
        elif result == "mega_win":
            add(view.user.id, 300)
            status = "MEGA WIN +300"
        else:
            add(view.user.id, -70)
            status = "LOSE -70"

        await interaction.message.edit(content=status, view=view)

        await asyncio.sleep(1)

        view.cooldown = False
        self.disabled = False

        await interaction.message.edit(view=view)


async def start_slots(ctx):
    view = SlotsView(ctx.author)

    msg = await ctx.respond("Slots ready", view=view)
    view.message = await msg.original_response()
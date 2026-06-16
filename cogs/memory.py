import discord
import asyncio
from games.memory import generate_board


class MemoryButton(discord.ui.Button):
    def __init__(self, index: int):
        super().__init__(
            label="❓",
            style=discord.ButtonStyle.secondary,
            row=index // 4
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: MemoryView = self.view

        if interaction.user != view.user:
            return await interaction.response.send_message("Not your game", ephemeral=True)

        if view.locked or view.revealed[self.index]:
            return await interaction.response.defer()

        await view.pick(interaction, self.index)


class MemoryView(discord.ui.View):
    def __init__(self, board, user):
        super().__init__(timeout=120)

        self.board = board
        self.user = user

        self.revealed = [False] * len(board)
        self.first = None
        self.second = None
        self.locked = False

        self.message = None

        for i in range(len(board)):
            self.add_item(MemoryButton(i))

    async def sync(self, interaction=None):
        if interaction:
            await interaction.response.edit_message(view=self)
        elif self.message:
            await self.message.edit(view=self)

    async def pick(self, interaction: discord.Interaction, index: int):
        self.locked = True

        btn = self.children[index]
        btn.label = self.board[index]
        btn.disabled = True

        if self.first is None:
            self.first = index
            self.locked = False
            await self.sync(interaction)
            return

        self.second = index

        await self.sync(interaction)

        await asyncio.sleep(0.8)

        await self.resolve()

    async def resolve(self):
        i, j = self.first, self.second

        b1, b2 = self.children[i], self.children[j]

        if self.board[i] == self.board[j]:
            b1.style = discord.ButtonStyle.success
            b2.style = discord.ButtonStyle.success

            self.revealed[i] = True
            self.revealed[j] = True
        else:
            b1.style = discord.ButtonStyle.danger
            b2.style = discord.ButtonStyle.danger

            await self.sync()

            await asyncio.sleep(0.6)

            b1.label = "❓"
            b2.label = "❓"

            b1.style = discord.ButtonStyle.secondary
            b2.style = discord.ButtonStyle.secondary

            b1.disabled = False
            b2.disabled = False

        self.first = None
        self.second = None
        self.locked = False

        await self.sync()

        if all(self.revealed):
            await self.finish()

    async def finish(self):
        for c in self.children:
            c.disabled = True

        await self.sync()

        if self.message:
            await self.message.edit(
                embed=discord.Embed(
                    title="🧠 Memory Complete",
                    description="All pairs found!",
                    color=0x00ffcc
                ),
                view=self
            )


async def start_memory(ctx):
    board = generate_board()
    view = MemoryView(board, ctx.author)

    embed = discord.Embed(
        title="🧠 Memory Game",
        description="Find all matching pairs",
        color=0x00ffcc
    )

    msg = await ctx.respond(embed=embed, view=view)
    view.message = await msg.original_response()
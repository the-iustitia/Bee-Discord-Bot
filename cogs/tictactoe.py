import discord
import asyncio
from utils.economy import add
from games.tictactoe import check_winner, empty_cells, bot_move


class TTTView(discord.ui.View):
    def __init__(self, p1, p2=None):
        super().__init__(timeout=180)

        self.p1 = p1
        self.p2 = p2
        self.vs_bot = p2 is None

        self.board = [None] * 9
        self.turn = p1

        self.locked = False
        self.active = True

        for i in range(9):
            self.add_item(TTTButton(i))

        self.add_item(RematchButton())

    def symbol(self, user):
        return "X" if user == self.p1 else "O"

    def allowed(self, user):
        if self.vs_bot:
            return user == self.p1
        return user in [self.p1, self.p2]

    def is_turn(self, user):
        return self.vs_bot or user == self.turn

    def switch(self):
        if not self.vs_bot:
            self.turn = self.p2 if self.turn == self.p1 else self.p1

    def disable_all(self):
        self.active = False
        for c in self.children:
            if isinstance(c, TTTButton):
                c.disabled = True


class TTTButton(discord.ui.Button):
    def __init__(self, index):
        super().__init__(
            label="⬜",
            style=discord.ButtonStyle.secondary,
            row=index // 3
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: TTTView = self.view

        if not view.active or view.locked:
            return await interaction.response.defer()

        if not view.allowed(interaction.user):
            return await interaction.response.send_message(
                "You are not part of this game",
                ephemeral=True
            )

        if not view.is_turn(interaction.user):
            return await interaction.response.send_message(
                "Not your turn",
                ephemeral=True
            )

        if view.board[self.index] is not None:
            return await interaction.response.defer()

        view.locked = True

        # PLAYER MOVE
        view.board[self.index] = view.symbol(interaction.user)
        self.label = view.board[self.index]
        self.disabled = True

        winner = check_winner(view.board)

        if winner:
            view.disable_all()

            if view.vs_bot:
                add(view.p1.id, 10)
                msg = "You win +10"
            else:
                add(interaction.user.id, 10)
                msg = f"{interaction.user.mention} wins +10"

            await interaction.response.edit_message(content=msg, view=view)
            view.locked = False
            return

        if not empty_cells(view.board):
            view.disable_all()
            await interaction.response.edit_message(content="Draw", view=view)
            view.locked = False
            return

        # BOT MOVE
        if view.vs_bot:
            await asyncio.sleep(0.3)

            move = bot_move(view.board)

            if move is not None:
                view.board[move] = "O"
                view.children[move].label = "O"
                view.children[move].disabled = True

            winner = check_winner(view.board)

            if winner:
                add(view.p1.id, -5)
                view.disable_all()
                await interaction.response.edit_message(content="Bot wins -5", view=view)
                view.locked = False
                return

            if not empty_cells(view.board):
                view.disable_all()
                await interaction.response.edit_message(content="Draw", view=view)
                view.locked = False
                return

        view.switch()

        await interaction.response.edit_message(view=view)

        await asyncio.sleep(0.05)
        view.locked = False


class RematchButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Rematch",
            style=discord.ButtonStyle.success,
            row=3
        )

    async def callback(self, interaction: discord.Interaction):
        view: TTTView = self.view

        if not view.vs_bot:
            if interaction.user not in [view.p1, view.p2]:
                return await interaction.response.send_message(
                    "Not allowed",
                    ephemeral=True
                )

        new_view = TTTView(view.p1, None if view.vs_bot else view.p2)

        embed = discord.Embed(
            title="Tic Tac Toe",
            description="New game started",
            color=0x00ffcc
        )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=new_view
        )


async def start_ttt(ctx, mode, opponent=None):
    view = TTTView(ctx.author, None if mode == "bot" else opponent)

    embed = discord.Embed(
        title="Tic Tac Toe",
        description="Bot mode" if mode == "bot" else f"PvP vs {opponent}",
        color=0x00ffcc
    )

    await ctx.respond(embed=embed, view=view)
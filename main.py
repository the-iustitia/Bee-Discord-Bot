from typing import List
import discord
from discord.ext import commands,tasks
from discord import Option, IntegrationType
from discord.ui import Modal, InputText, View, Button
import random
import requests
import asyncio
from datetime import datetime
import pytz
import aiohttp
import os
import json
from typing import NoReturn
import pycountry
from PIL import Image, ImageDraw, ImageFont
import io
from io import BytesIO
from discord import File
from dotenv import load_dotenv

def load_json(filename):
    path = os.path.join('Json', filename)
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
flags = load_json('flags.json')
truths = load_json('truths.json')
dares = load_json('dares.json')
trivia_questions = load_json('trivia_questions.json')
questions = load_json("questions.json")

bot = commands.Bot(command_prefix = "!")
SPECIFIC_USER_ID = 1121059810717225030

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.slash_command(name='profile', description='Displays user passport information', integration_types = {
        IntegrationType.user_install,
        IntegrationType.guild_install
})
async def user_info(ctx, user: Option(discord.Member, description='Select a user', required=False)):
    user = user or ctx.author
    
    embed = discord.Embed(title=f"{user}'s User Information", color=discord.Color.from_rgb(255, 255, 0))
    embed.set_thumbnail(url=user.avatar.url)
    
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="Discriminator", value=f"#{user.discriminator}", inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    
    if user.nick:
        embed.add_field(name="Nickname", value=user.nick, inline=True)
    
    roles = [role.mention for role in user.roles[1:]]
    embed.add_field(name="Roles", value=", ".join(roles) if roles else "No roles", inline=False)
    
    await ctx.respond(embed=embed)

@bot.slash_command(name='server', description='Displays information about the server')
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Information for {guild.name}", color=discord.Color.from_rgb(255, 255, 0))
    
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    
    await ctx.respond(embed=embed)

@bot.slash_command(name='fun_fact', description='Get a random fun fact', integration_types = {
  IntegrationType.guild_install,
  IntegrationType.user_install
})
async def fun_fact(ctx):
    try:
        if ctx.guild is None or ctx.channel is None:
            await ctx.respond("This command can only be used in a server channel.")
            return
        
        if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.respond("I have no permission to send messages in this channel.")
            return
        
        await ctx.channel.trigger_typing()
        
        response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
        response.raise_for_status()
        data = response.json()
        fact_text = data['text']
        
        embed = discord.Embed(title="Fun Fact", description=fact_text, color=discord.Color.from_rgb(255, 255, 0))
        await ctx.respond(embed=embed)
        
    except requests.exceptions.RequestException as e:
        await ctx.respond(f"An error occurred while fetching a fun fact: {e}")
    except discord.errors.Forbidden:
        await ctx.respond("I have no access.")
    except Exception as e:
        await ctx.respond(f"Error: {e}")

@bot.slash_command(name='avatar', description='Displays the avatar of the specified user', integration_types = {
    IntegrationType.user_install,
    IntegrationType.guild_install
  })
async def avatar(ctx, user: Option(discord.Member, description='Select a user', required=False)):
    user = user or ctx.author
    
    embed = discord.Embed(title=f"{user}'s Avatar", color=discord.Color.from_rgb(255, 255, 0))
    embed.set_image(url=user.avatar.url)
    
    await ctx.respond(embed=embed)
    
@bot.slash_command(name='kick', description='Kick a user from the server')
async def kick(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.ban_members or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        try:
            await user.kick()
            await ctx.respond(f"{user.mention} has been kicked from the server.")
        except discord.Forbidden:
            await ctx.respond("I do not have permission to kick this user. Please check the bot's role permissions.")
        except discord.HTTPException as e:
            print(f"Failed to kick user: {e}")
            await ctx.respond("Failed to kick the user. Please try again later.")
    else:
        await ctx.respond("You do not have permission to kick members.")

@bot.slash_command(name='warn', description='Warn a user for violating server rules')
async def warn(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.administrator or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        if user == ctx.author:
            await ctx.respond("You cannot warn yourself.")
            return
        elif user.top_role >= ctx.author.top_role:
            await ctx.respond("You cannot warn this user due to role hierarchy.")
            return

        embed = discord.Embed(
            title="Warning",
            description=f"You have been warned for violating server rules in {ctx.guild.name}. Please adhere to the rules.",
            color=discord.Color.gold()
        )

        try:
            await user.send(embed=embed)
            await ctx.respond(f"{user.mention} has been warned.")
        except discord.Forbidden:
            await ctx.respond(f"{user.mention} has been warned, but their DMs are closed.")
        except discord.HTTPException as e:
            print(f"Failed to warn user: {e}")
            await ctx.respond("Failed to send the warning. Please try again later.")
    else:
        await ctx.respond("You do not have permission to warn members.")

MAX_TEMP_BAN_DURATION = 7  # Maximum duration for temporary bans in days
DEFAULT_BAN_DURATION = 1  # Default duration for temporary bans (if not specified)

@bot.slash_command(name='ban', description='Ban a user from the server')
async def ban(ctx, user: Option(discord.Member, description='Select a user'), duration: Option(str, description="Duration of the temporary ban (e.g. 1h, 30m, 2d)", required=False)):
    # Check permissions
    if ctx.author.guild_permissions.ban_members or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        if user == ctx.author:
            await ctx.respond("You cannot ban yourself.")
        elif user.top_role >= ctx.author.top_role:
            await ctx.respond("You cannot ban this user due to role hierarchy.")
        else:
            # Handle temporary ban logic if duration is provided
            if duration:
                # Try to parse the duration
                duration_match = re.match(r'(\d+)([smhd])', duration.strip().lower())
                if duration_match:
                    amount, unit = duration_match.groups()
                    amount = int(amount)

                    # Convert the duration to seconds
                    if unit == 's':
                        ban_duration = timedelta(seconds=amount)
                    elif unit == 'm':
                        ban_duration = timedelta(minutes=amount)
                    elif unit == 'h':
                        ban_duration = timedelta(hours=amount)
                    elif unit == 'd':
                        ban_duration = timedelta(days=amount)
                    else:
                        await ctx.respond("Invalid time unit. Use 's' for seconds, 'm' for minutes, 'h' for hours, or 'd' for days.")
                        return

                    # Ensure the ban duration doesn't exceed the max limit
                    if ban_duration > timedelta(days=MAX_TEMP_BAN_DURATION):
                        await ctx.respond(f"Temporary ban duration cannot exceed {MAX_TEMP_BAN_DURATION} days.")
                        return

                    # Unban time after the specified duration
                    unban_time = datetime.utcnow() + ban_duration
                    try:
                        await user.ban(reason=f"Temporary ban for {duration}")
                        await ctx.respond(f"{user.mention} has been temporarily banned for {duration}.")

                        # Schedule automatic unban (using a simple task scheduler or delayed task)
                        # Example: Using asyncio.sleep for a simple demonstration
                        await asyncio.sleep(ban_duration.total_seconds())
                        await ctx.guild.unban(user)
                        print(f"Unbanned {user.mention} after temporary ban duration.")
                    except discord.Forbidden:
                        await ctx.respond("I do not have permission to ban this user. Please check the bot's role permissions.")
                    except discord.HTTPException as e:
                        print(f"Failed to ban user: {e}")
                        await ctx.respond("Failed to ban the user. Please try again later.")
                else:
                    await ctx.respond("Invalid duration format. Please use a valid format like '1h', '30m', or '2d'.")
            else:
                # If no duration is specified, perform a permanent ban
                try:
                    await user.ban()
                    await ctx.respond(f"{user.mention} has been permanently banned from the server.")
                except discord.Forbidden:
                    await ctx.respond("I do not have permission to ban this user. Please check the bot's role permissions.")
                except discord.HTTPException as e:
                    print(f"Failed to ban user: {e}")
                    await ctx.respond("Failed to ban the user. Please try again later.")

    else:
        await ctx.respond("You do not have permission to ban members.")

@bot.slash_command(name='mute', description='Mute a user in the server')
async def mute(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.manage_roles or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(name="Muted", reason="For muting users", permissions=discord.Permissions(send_messages=False, speak=False))
                
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)

                await ctx.respond("Muted role created successfully.")
            except discord.Forbidden:
                await ctx.respond("I do not have permissions to create roles. Please ask an administrator to create a role named 'Muted'.")
                return
            except discord.HTTPException as e:
                print(f"Failed to create the 'Muted' role: {e}")
                await ctx.respond("Failed to create the 'Muted' role. Please check server settings or try again later.")
                return
        
        if muted_role in user.roles:
            await ctx.respond(f"{user.mention} is already muted.")
        else:
            try:
                await user.add_roles(muted_role)
                await ctx.respond(f"{user.mention} has been muted.")
            except discord.Forbidden:
                await ctx.respond("I do not have permission to mute this user. Please check the bot's role permissions.")
            except discord.HTTPException as e:
                print(f"Failed to mute user: {e}")
                await ctx.respond("Failed to mute the user. Please try again later.")
    else:
        await ctx.respond("You do not have permission to mute members.")

@bot.slash_command(name='unmute', description='Unmute a user in the server')
async def unmute(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.manage_roles or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.respond("The 'Muted' role does not exist. Please create it first.")
            return
        
        if muted_role not in user.roles:
            await ctx.respond(f"{user.mention} is not muted.")
        else:
            try:
                await user.remove_roles(muted_role)
                await ctx.respond(f"{user.mention} has been unmuted.")
            except discord.Forbidden:
                await ctx.respond("I do not have permission to unmute this user. Please check the bot's role permissions.")
            except discord.HTTPException as e:
                print(f"Failed to unmute user: {e}")
                await ctx.respond("Failed to unmute the user. Please try again later.")
    else:
        await ctx.respond("You do not have permission to unmute members.")

@bot.slash_command(name='unban', description='Unban a user from the server')
async def unban(ctx, user: Option(str, description='User ID to unban')):
    if ctx.author.guild_permissions.ban_members or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        try:
            user_obj = await bot.fetch_user(user)
            await ctx.guild.unban(user_obj)
            await ctx.respond(f"{user_obj.mention} has been unbanned from the server.")
        except discord.NotFound:
            await ctx.respond("User not found. Please provide a valid User ID.")
        except discord.Forbidden:
            await ctx.respond("I do not have permission to unban this user. Please check the bot's role permissions.")
        except discord.HTTPException as e:
            print(f"Failed to unban user: {e}")
            await ctx.respond("Failed to unban the user. Please try again later.")
    else:
        await ctx.respond("You do not have permission to unban members.")

@bot.slash_command(name='clear', description='Clear messages in a chat')
async def clear(ctx: discord.ApplicationContext, amount_or_all: str):
    if ctx.author.guild_permissions.manage_messages or ctx.author.id == ctx.guild.owner_id or ctx.author.id == SPECIFIC_USER_ID:
        try:
            if amount_or_all.lower() == 'all':
                await ctx.channel.purge()
                await ctx.respond("All messages have been deleted.", delete_after=5)
            else:
                amount = int(amount_or_all)
                await ctx.channel.purge(limit=amount)
                await ctx.respond(f"{amount} messages have been deleted.", delete_after=5)
        except ValueError:
            await ctx.respond("Invalid command usage. Please provide a number or 'all'.")
        except discord.Forbidden:
            await ctx.respond("I do not have permission to delete messages. Please check the bot's role permissions.")
        except discord.HTTPException as e:
            print(f"Failed to clear messages: {e}")
            await ctx.respond("Failed to clear messages. Please try again later.")
    else:
        await ctx.respond("You do not have permission to delete messages.")

@bot.slash_command(name='trivia', description='Answer a random trivia question')
async def trivia(ctx):
    question_data = random.choice(trivia_questions)
    question = question_data['question']
    choices = question_data['choices']
    correct_answer = question_data['answer']

    buttons = [Button(label=choice, style=discord.ButtonStyle.primary) for choice in choices]

    async def button_callback(interaction: discord.Interaction):
        selected_answer = interaction.data['custom_id']
        if selected_answer == correct_answer:
            await interaction.response.send_message("Correct! 🎉", ephemeral=True)
        else:
            await interaction.response.send_message(f"Wrong answer. The correct answer was {correct_answer}.", ephemeral=True)

    view = View()
    for button, choice in zip(buttons, choices):
        button.custom_id = choice
        button.callback = button_callback
        view.add_item(button)

    await ctx.respond(f"Trivia Question: {question}", view=view)

class RPSButtonView(discord.ui.View):
    def __init__(self, ctx, user_choice, bot_choice):
        super().__init__(timeout=15)
        self.ctx = ctx
        self.user_choice = user_choice
        self.bot_choice = bot_choice

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.blurple)
    async def rock_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_interaction(interaction, "rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.green)
    async def paper_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_interaction(interaction, "paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.red)
    async def scissors_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_interaction(interaction, "scissors")

    async def handle_interaction(self, interaction: discord.Interaction, user_choice):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        bot_choice = random.choice(['rock', 'paper', 'scissors'])

        if user_choice == bot_choice:
            result = "It's a tie!"
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'paper' and bot_choice == 'rock') or \
             (user_choice == 'scissors' and bot_choice == 'paper'):
            result = "You win! 🎉"
        else:
            result = "You lose! 😢"

        await interaction.response.edit_message(content=f"You chose {user_choice}, I chose {bot_choice}. {result}", view=None)

@bot.slash_command(name='rps', description='Play Rock-Paper-Scissors', integration_types = {
        IntegrationType.user_install,
        IntegrationType.guild_install
})
async def rock_paper_scissors(ctx):
    try:
        view = RPSButtonView(ctx, None, None)
        await ctx.respond("Choose Rock, Paper, or Scissors:", view=view)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

class TruthOrDareButtonView(discord.ui.View):
    def __init__(self, ctx, truths, dares):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.result = None
        self.truths = truths
        self.dares = dares

    @discord.ui.button(label="Truth", style=discord.ButtonStyle.green)
    async def truth_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return
        truth = random.choice(self.truths)
        await interaction.response.edit_message(content=f"Truth: {truth}")

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.red)
    async def dare_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return
        dare = random.choice(self.dares)
        await interaction.response.edit_message(content=f"Dare: {dare}")

@bot.slash_command(name='truth_or_dare', description='Play a game of Truth or Dare', integration_types = {
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def truth_or_dare(ctx):
    view = TruthOrDareButtonView(ctx, truths, dares)
    await ctx.respond("Truth or Dare? Click a button to choose.", view=view)

class CasinoView(View):
    def __init__(self):
        super().__init__()
        self.add_item(SpinButton())

class SpinButton(Button):
    def __init__(self):
        super().__init__(label="Spin", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        slots = ["🍒", "🍋", "🍊", "🍇", "🍉", "🍓"]
        result = [random.choice(slots) for _ in range(3)]
        
        if len(set(result)) == 1:
            if result[0] == "🍒":
                message = f"{' '.join(result)} - Jackpot! 🍒 You hit the cherry jackpot! 🎉"
            elif result[0] == "🍓":
                message = f"{' '.join(result)} - Strawberry Surprise! 🍓 Enjoy your bonus!"
            else:
                message = f"{' '.join(result)} - You won big!"
        else:
            if "🍒" in result and "🍋" in result:
                message = f"{' '.join(result)} - Almost there! 🍒🍋 Keep spinning!"
            else:
                message = f"{' '.join(result)} - Better luck next time!"

        await interaction.response.send_message(message, ephemeral=False)

@bot.slash_command(name='casino', description='Start a casino game', integration_types={
    discord.enums.IntegrationType.user_install,
    discord.enums.IntegrationType.guild_install
})
async def casino(ctx):
    view = CasinoView()
    await ctx.respond("Welcome to the Casino! Spin the slot machine and see if you win big!", view=view)

player_win_streak = {}

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O) or view.locked:
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
                player_win_streak[interaction.user.id] = player_win_streak.get(interaction.user.id, 0) + 1
                if player_win_streak[interaction.user.id] == 5:
                    content += ' 🎉 Congratulations! You are the Tournament Champion!'
                    player_win_streak[interaction.user.id] = 0
            elif winner == view.O:
                content = 'O won!'
                player_win_streak[interaction.user.id] = 0
            else:
                content = "It's a tie!"
                player_win_streak[interaction.user.id] = 0

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

        if view.current_player == view.O and view.opponent == "bot":
            await view.bot_move(interaction)

class TicTacToeView(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, opponent, difficulty):
        super().__init__()
        self.current_player = self.X
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.opponent = opponent
        self.locked = False
        self.difficulty = difficulty

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        rdiag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if rdiag == 3:
            return self.O
        elif rdiag == -3:
            return self.X

        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

    def is_moves_left(self):
        for row in self.board:
            if 0 in row:
                return True
        return False

    def evaluate(self):
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2]:
                if self.board[row][0] == self.O:
                    return 10
                elif self.board[row][0] == self.X:
                    return -10

        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col]:
                if self.board[0][col] == self.O:
                    return 10
                elif self.board[0][col] == self.X:
                    return -10

        if self.board[0][0] == self.board[1][1] == self.board[2][2]:
            if self.board[0][0] == self.O:
                return 10
            elif self.board[0][0] == self.X:
                return -10

        if self.board[0][2] == self.board[1][1] == self.board[2][0]:
            if self.board[0][2] == self.O:
                return 10
            elif self.board[0][2] == self.X:
                return -10

        return 0

    def minimax(self, depth, is_max):
        score = self.evaluate()

        if score == 10:
            return score - depth

        if score == -10:
            return score + depth

        if not self.is_moves_left():
            return 0

        if is_max:
            best = -1000

            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == 0:
                        self.board[i][j] = self.O
                        best = max(best, self.minimax(depth + 1, not is_max))
                        self.board[i][j] = 0
            return best

        else:
            best = 1000

            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == 0:
                        self.board[i][j] = self.X
                        best = min(best, self.minimax(depth + 1, not is_max))
                        self.board[i][j] = 0
            return best

    def find_best_move(self):
        if self.difficulty == 'easy':
            import random
            empty_cells = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == 0]
            return random.choice(empty_cells) if empty_cells else (-1, -1)
        
        best_val = -1000
        best_move = (-1, -1)

        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    self.board[i][j] = self.O
                    move_val = self.minimax(0, False)
                    self.board[i][j] = 0

                    if move_val > best_val:
                        best_move = (i, j)
                        best_val = move_val

        return best_move

    async def bot_move(self, interaction: discord.Interaction):
        row, col = self.find_best_move()
        self.board[row][col] = self.O
        for child in self.children:
            if isinstance(child, TicTacToeButton):
                if child.x == col and child.y == row:
                    child.style = discord.ButtonStyle.success
                    child.label = 'O'
                    child.disabled = True
                    break

        self.current_player = self.X
        winner = self.check_winner()
        content = "It is now X's turn"

        if winner is not None:
            if winner == self.X:
                content = 'X won!'
                player_win_streak[interaction.user.id] = player_win_streak.get(interaction.user.id, 0) + 1
                if player_win_streak[interaction.user.id] == 5:
                    content += ' 🎉 Congratulations! You are the Tournament Champion!'
                    player_win_streak[interaction.user.id] = 0
            elif winner == self.O:
                content = 'O won!'
                player_win_streak[interaction.user.id] = 0
            else:
                content = "It's a tie!"
                player_win_streak[interaction.user.id] = 0

            for child in self.children:
                child.disabled = True

            self.stop()

        await interaction.edit_original_response(content=content, view=self)

@bot.slash_command(
    name='tic_tac_toe', description='Play a game of Tic-Tac-Toe', integration_types = {
        IntegrationType.user_install,
        IntegrationType.guild_install
    })
async def tic_tac_toe(
    ctx, 
    opponent: Option(str, "Choose your opponent", choices=["bot", "player"]),
    difficulty: Option(str, "Choose bot difficulty", choices=["easy", "medium", "hard"]) = "medium"
):
    await ctx.respond(f"Tic Tac Toe: X goes first. Difficulty: {difficulty}", view=TicTacToeView(opponent, difficulty))

@bot.slash_command(name='wyr', description='Play a game of Would You Rather', integration_types = {
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def would_you_rather(ctx):
    question_data = random.choice(questions)
    question = question_data['question']
    option1 = question_data['option1']
    option2 = question_data['option2']

    embed = discord.Embed(title="Would You Rather", description=question, color=discord.Color.blue())
    embed.add_field(name="Option 1", value=option1)
    embed.add_field(name="Option 2", value=option2)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label=option1, style=discord.ButtonStyle.primary, custom_id='option1'))
    view.add_item(discord.ui.Button(label=option2, style=discord.ButtonStyle.secondary, custom_id='option2'))

    async def button_callback(interaction: discord.Interaction):
        if interaction.custom_id == 'option1':
            await interaction.response.send_message(f"You chose: {option1}", ephemeral=True)
        else:
            await interaction.response.send_message(f"You chose: {option2}", ephemeral=True)

    for item in view.children:
        item.callback = button_callback

    await ctx.respond(embed=embed, view=view)

class MemoryButton(discord.ui.Button):
    def __init__(self, label, row, column):
        super().__init__(style=discord.ButtonStyle.secondary, label='?', row=row)
        self.row = row
        self.column = column
        self.content = label
        self.revealed = False

    async def callback(self, interaction: discord.Interaction):
        view: MemoryGameView = self.view
        if self.revealed or view.locked:
            return

        self.revealed = True
        self.label = self.content
        self.style = discord.ButtonStyle.primary
        await interaction.response.edit_message(view=view)

        if view.first_selection is None:
            view.first_selection = self
        else:
            view.locked = True
            await asyncio.sleep(1)

            if self.content == view.first_selection.content:
                self.style = discord.ButtonStyle.success
                view.first_selection.style = discord.ButtonStyle.success
                view.matches += 1
                if view.matches == len(view.board) // 2:
                    await interaction.followup.send("You have matched all pairs! 🎉")
                    view.stop()
                    if random.randint(1, 1000) == 1:
                        await interaction.followup.send("Congratulations! You've found the secret item! 🎉")
            else:
                self.label = '?'
                self.style = discord.ButtonStyle.secondary
                view.first_selection.label = '?'
                view.first_selection.style = discord.ButtonStyle.secondary

            self.revealed = False
            view.first_selection.revealed = False
            view.first_selection = None
            view.locked = False

            await interaction.edit_original_response(view=view)

class MemoryGameView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.board = ['🍎', '🍎', '🍌', '🍌', '🍒', '🍒', '🍇', '🍇', '🍉', '🍉', '🥭', '🥭', '🍓', '🍓', '🍍', '🍍', '🍊', '🍊', '🐝', '🐝']
        
        if random.randint(1, 1000) == 1:
            self.board.append('🎉')
            self.board.append('🎉')
        
        random.shuffle(self.board)
        self.first_selection = None
        self.matches = 0
        self.locked = False

        for i, label in enumerate(self.board):
            self.add_item(MemoryButton(label, i // 4, i % 5))

@bot.slash_command(name='memory_game', description='Play a memory game', integration_types ={
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def memory_game(ctx):
    await ctx.respond("Memory Game: Find all pairs!", view=MemoryGameView())

@bot.slash_command(name="giveaway", description="Starts a giveaway")
async def _giveaway(ctx: discord.ApplicationContext, winners: int, prize: str):
    if ctx.author.guild_permissions.administrator:
        guild = bot.get_guild(ctx.guild_id)
        participants = [member for member in guild.members if not member.bot]

        if len(participants) == 0:
            await ctx.respond("Not enough participants for the giveaway.")
            return
        
        winners_count = min(winners, len(participants))
        
        print(f"Количество победителей: {winners_count}")

        winners_list = random.sample(participants, winners_count)
        winners_text = "\n".join([winner.mention for winner in winners_list])

        win_message = f"Congratulations to the winners!\n{winners_text}"

        embed = discord.Embed(title="🎉 Giveaway Results 🎉",
                              description=f"**Prize:** {prize}\n**Number of winners:** {winners_count}",
                              color=discord.Color.from_rgb(255, 255, 0))
        embed.add_field(name="Winners:", value=win_message)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("You do not have permission to start a giveaway.")

timezones = {
    'UTC': 'UTC',
    'GMT': 'Etc/GMT',
    'CET': 'CET',
    'EET': 'EET',
    'IST': 'Asia/Kolkata',
    'CST': 'America/Chicago',
    'JST': 'Asia/Tokyo',
    'AEST': 'Australia/Sydney',
}

@bot.slash_command(name="time", description="Send time in different time zones", integration_types = {
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def time(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="Current Times in Various Timezones",
        color=discord.Color.blue()
    )

    for zone, tz in timezones.items():
        timezone = pytz.timezone(tz)
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        embed.add_field(name=zone, value=current_time, inline=False)

    await ctx.respond(embed=embed)

@tasks.loop(minutes=1)
async def update_time_status():
    now_utc = datetime.now(pytz.timezone('UTC')).strftime('%H:%M')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"UTC Time: {now_utc}"))

@update_time_status.before_loop
async def before_update_time_status():
    await bot.wait_until_ready()

update_time_status.start()

@bot.slash_command(name='coin', description='Flips a coin and shows the result (heads or tails)', integration_types = {
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def flip_coin(ctx: discord.ApplicationContext):
    if random.randint(1, 10000) == 1:
        await ctx.respond("Oops! The coin rolled under the couch!")
    else:
        result = random.choice(['heads', 'tails'])
        await ctx.respond(f'The coin landed on: {result}')

def get_flag_url(country_name):
    country = pycountry.countries.get(name=country_name)
    if not country:
        matches = [c for c in pycountry.countries if country_name.lower() in c.name.lower()]
        if matches:
            country = matches[0]
        else:
            return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"  # запасной флаг
    return f"https://flagcdn.com/w320/{country.alpha_2.lower()}.png"

class TriviaButton(Button):
    def __init__(self, label, correct_answer):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct_answer = correct_answer

    async def callback(self, interaction: discord.Interaction):
        if self.label == self.correct_answer:
            await interaction.response.send_message(f"✅ Правильно! Это {self.correct_answer}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Неправильно. Правильный ответ: {self.correct_answer}.", ephemeral=True)
        # Отключаем кнопки
        for child in self.view.children:
            child.disabled = True
        await interaction.message.edit(view=self.view)

class TriviaView(View):
    def __init__(self, correct_answer, options):
        super().__init__(timeout=20)
        random.shuffle(options)
        for option in options:
            self.add_item(TriviaButton(label=option, correct_answer=correct_answer))

@bot.slash_command(name='flaggame', description='Угадай страну по флагу', integration_types ={
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def flag_game(ctx):
    all_countries = [country.name for country in pycountry.countries]
    correct_country = random.choice(all_countries)

    # Получаем 3 неправильных варианта
    wrong_countries = random.sample([c for c in all_countries if c != correct_country], 3)
    options = [correct_country] + wrong_countries

    # Получаем URL флага
    flag_url = get_flag_url(correct_country)

    embed = discord.Embed(
        title="Угадай страну по флагу!",
        description="Выберите правильный вариант:",
        color=discord.Color.blue()
    )
    embed.set_image(url=flag_url)
    embed.set_footer(text="Нажмите на один из вариантов ниже.")

    view = TriviaView(correct_answer=correct_country, options=options)
    await ctx.respond(embed=embed, view=view)

@bot.slash_command(name="joke", description="Sending a random joke", integration_types = {
    IntegrationType.user_install,
    IntegrationType.guild_install
})
async def joke(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["type"] == "single":
                            joke = data["joke"]
                        else:
                            joke = f'{data["setup"]} - {data["delivery"]}'
                        await ctx.respond(joke)
                    else:
                        await ctx.respond("Failed to fetch joke, please try again later.")
            except aiohttp.ClientError as e:
                await ctx.respond(f"An error occurred while fetching the joke: {e}")
    except Exception as e:
        await ctx.respond(f"An unexpected error occurred: {e}")

suits = {'Hearts': '♥️', 'Diamonds': '♦️', 'Clubs': '♣️', 'Spades': '♠️'}
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

def load_balance():
    try:
        with open('economy.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_balance(balance_data):
    with open('economy.json', 'w') as f:
        json.dump(balance_data, f)

def create_deck():
    return [{'suit': suit, 'rank': rank} for suit in suits.keys() for rank in ranks]

def calculate_hand_value(hand):
    value = sum(values[card['rank']] for card in hand)
    num_aces = sum(1 for card in hand if card['rank'] == 'A')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

def format_hand(hand):
    return ' '.join(f"{card['rank']}{suits[card['suit']]}" for card in hand)

def format_game_state(player_hand, dealer_hand, hidden=True):
    player_val = calculate_hand_value(player_hand)
    player_line = f"🧑 You: [{format_hand(player_hand)}] (Total: {player_val})"
    
    if hidden:
        # Показываем только первую карту дилера
        dealer_line = f"🤖 Bot: [{format_hand([dealer_hand[0]])}] ❓"
    else:
        # Показываем обе карты дилера
        dealer_val = calculate_hand_value(dealer_hand)
        dealer_line = f"🤖 Bot: [{format_hand(dealer_hand)}] (Total: {dealer_val})"
        
    return f"{player_line}\n{dealer_line}"

def create_embed(title, description, color=0xFFFF00):
    return discord.Embed(
        title=title,
        description=description,
        color=color
    )

@bot.slash_command(name='blackjack', description="Play a game of Blackjack")
async def blackjack(ctx):
    balance_data = load_balance()
    player_id = str(ctx.user.id)

    if player_id not in balance_data:
        balance_data[player_id] = 1000

    if balance_data[player_id] < 10:
        embed = create_embed("💸 Not enough coins!", f"Balance: {balance_data[player_id]}")
        await ctx.send(embed=embed, ephemeral=True)
        return

    balance_data[player_id] -= 10
    save_balance(balance_data)

    await ctx.defer()

    deck = create_deck()
    random.shuffle(deck)

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    class BlackjackView(View):
        def __init__(self, ctx, player_hand, dealer_hand, deck, player_id, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ctx = ctx
            self.player_hand = player_hand
            self.dealer_hand = dealer_hand
            self.deck = deck
            self.finished = False
            self.player_id = player_id

        @discord.ui.button(label='Hit', style=discord.ButtonStyle.primary)
        async def hit_button(self, button: Button, interaction: discord.Interaction):
            if self.finished:
                return

            self.player_hand.append(self.deck.pop())
            player_value = calculate_hand_value(self.player_hand)

            if player_value > 21:
                self.finished = True
                result = format_game_state(self.player_hand, self.dealer_hand, hidden=False)
                embed = create_embed(
                    "💥 You went over 21! Bot wins.",
                    f"{result}\n\n💥 You went over 21! Bot wins."
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

            embed = create_embed(
                "Your Turn",
                format_game_state(self.player_hand, self.dealer_hand)
            )
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label='Stand', style=discord.ButtonStyle.secondary)
        async def stand_button(self, button: Button, interaction: discord.Interaction):
            if self.finished:
                return

            self.finished = True

            while calculate_hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())

            player_value = calculate_hand_value(self.player_hand)
            dealer_value = calculate_hand_value(self.dealer_hand)

            result = format_game_state(self.player_hand, self.dealer_hand, hidden=False)

            if dealer_value > 21 or player_value > dealer_value:
                result += "\n\n🎉 You win!"
                balance_data[self.player_id] += 20
            elif dealer_value > player_value:
                result += "\n\n🤖 Bot wins!"
            else:
                result += "\n\n🤝 It's a draw!"

            save_balance(balance_data)

            embed = create_embed("Game Over", result)
            await interaction.response.edit_message(embed=embed, view=None)

    view = BlackjackView(ctx, player_hand, dealer_hand, deck, player_id)

    embed = create_embed(
        "🎰 Blackjack Started!",
        f"10 coins deducted.\n\n{format_game_state(player_hand, dealer_hand)}\n\nChoose your action:"
    )
    await ctx.followup.send(embed=embed, view=view)

load_dotenv()

BACKGROUND_FOLDER = "backgrounds"
FONT_PATH = "fonts/Impact.ttf"
FONT_SIZE = 300
TEXT_AREA_RATIO = 0.5

bot = commands.Bot()

@bot.slash_command(name="quote", description="Generate a quote image")
async def quote(
    ctx,
    text: Option(str, description="Quote text"),
    bg: Option(int, description="Background number (1–5)", choices=[1, 2, 3, 4, 5]),
    image_url: Option(str, required=False, description="Optional image URL to overlay") = None,
    dm: Option(bool, required=False, description="Send to DM instead of channel") = False
):
    await ctx.defer(ephemeral=True)

    try:
        bg_path = os.path.join(BACKGROUND_FOLDER, f"{bg}.jpg")
        if not os.path.exists(bg_path):
            await ctx.respond("Background is not found.")
            return

        img = Image.open(bg_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        # Параметры текста
        W, H = img.size
        text_width = int(W * TEXT_AREA_RATIO) - 40
        x = W - text_width - 40
        y = 40

        # Функция переноса текста
        def wrap_text(text, font, max_width):
            words = text.split()
            lines, line = [], ""
            for word in words:
                test_line = f"{line}{word} "
                if font.getlength(test_line) <= max_width:
                    line = test_line
                else:
                    lines.append(line.strip())
                    line = f"{word} "
            if line:
                lines.append(line.strip())
            return lines

        lines = wrap_text(text, font, text_width)

        def get_text_height(text, font):
            bbox = font.getbbox(text)
            return bbox[3] - bbox[1]

        # Рисуем строки
        for line in lines:
            draw.text((x, y), line, font=font, fill="white")
            y += get_text_height(line, font) + 10 

        output_path = "quote_output.png"
        img.save(output_path)

        with open(output_path, "rb") as f:
            file = File(f, filename="quote.png")
            if dm:
                await ctx.author.send(file=file)
                await ctx.respond("Quote sended in a DM.")
            else:
                await ctx.respond(file=file)

        os.remove(output_path)

    except Exception as e:
        await ctx.respond("Error with generate image.")
        print(f"[ERROR]: {e}")

if __name__ == "__main__":
    import asyncio
    bot.run('')
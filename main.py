from typing import List
import discord
from discord.ext import commands
from discord import Option
import requests
from discord.ui import Button, View
import random
import asyncio
from datetime import datetime
import pytz

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        if "429 Too Many Requests" in str(error):
            await asyncio.sleep(10)  # Задержка перед повторной попыткой
        else:
            raise error

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.slash_command(name='profile', description='Displays user passport information')
async def user_info(ctx, user: Option(discord.Member, description='Select a user', required=False)):
    user = user or ctx.author
    
    embed = discord.Embed(title=f"{user}'s User Information", color=discord.Color.from_rgb(0, 0, 0))
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
    embed = discord.Embed(title=f"Server Information for {guild.name}", color=discord.Color.from_rgb(0, 0, 0))
    
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    
    await ctx.respond(embed=embed)

@bot.slash_command(name='fun_fact', description='Get a random fun fact')
async def fun_fact(ctx):
    await ctx.channel.trigger_typing()
    try:
        response = requests.get('https://uselessfacts.jsph.pl/random.json')
        response.raise_for_status()
        data = response.json()
        fact_text = data['text']

        embed = discord.Embed(title="Fun Fact", description=fact_text, color=discord.Color.from_rgb(0, 0, 0))
        await ctx.respond(embed=embed)
    except requests.exceptions.RequestException as e:
        await ctx.respond(f"An error occurred while fetching a fun fact: {e}")

@bot.slash_command(name='avatar', description='Displays the avatar of the specified user')
async def avatar(ctx, user: Option(discord.Member, description='Select a user', required=False)):
    user = user or ctx.author
    
    embed = discord.Embed(title=f"{user}'s Avatar", color=discord.Color.from_rgb(0, 0, 0))
    embed.set_image(url=user.avatar.url)
    
    await ctx.respond(embed=embed)
    
@bot.command()
async def rules(ctx):
    embed = discord.Embed(
        title="Rules of the Server",
        description="Please familiarize yourself with these rules to maintain a pleasant and harmonious atmosphere on the server. Thank you for your understanding and for adhering to the rules! 🌟👮‍♂️",
        color=discord.Color.from_rgb(0, 0, 0)   
    )

    rules = [
        ("🚫 **No swearing**", "Use of offensive language."),
        ("🙏 **No blasphemy**", ""),
        ("🚫 **No insults**", "Disrespectful or offensive comments towards other participants."),
        ("🚫 **No discrimination**", "Displaying racist, sexist, or other forms of discrimination."),
        ("🔞 **No pornography**", "Posting or discussing pornographic content."),
        ("💥 **No violent content**", "Posting shocking or violent content."),
        ("🚫 **No racism**", "Expressing racist statements or behavior."),
        ("❤️ **Respect others**", "Unacceptable behavior towards other participants."),
        ("🎥 **No deceptive videos/photos**", "Posting videos or photos with the intent to deceive other participants."),
        ("🚫 **No spam**", "Repeated or mass posting of identical or meaningless messages."),
        ("🚫 **No inappropriate names**", "Using inappropriate or offensive profile names."),
        ("🚫 **No swastikas**", "Posting images of swastikas."),
        ("📢 **No unwanted advertising**", "Posting advertising material without server staff consent."),
        ("🗳️ **No discussion of politics**", "Discussion of politics, wars, or political actions."),
        ("🗨️ **Communicate in relevant channels**", "Chatting in inappropriate channels, such as asking for car settings in a meme channel.")
    ]

    for rule, violation in rules:
        embed.add_field(name=rule, value=violation, inline=False)

    await ctx.send(embed=embed)

@bot.slash_command(name='kick', description='Kick a user from the server')
async def kick(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.kick_members:
        await user.kick()
        await ctx.respond(f"{user.mention} has been kicked from the server.")
    else:
        await ctx.respond("You do not have permission to kick members.")

@bot.slash_command(name='warn', description='Warn a user for violating server rules')
async def warn(ctx, user: Option(discord.Member, description='Select a user')):
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
        await ctx.send(f"{user.mention}, you have been warned for violating server rules in {ctx.guild.name}. Please adhere to the rules.", embed=embed)

@bot.command()
async def say(ctx, *, message: str):
    if ctx.author.guild_permissions.kick_members:    
        await ctx.message.delete()
        await ctx.send(message)
    else:
        await ctx.respond("You do not have permission use this command.")    

@bot.slash_command(name='ban', description='Ban a user from the server')
async def ban(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.ban_members:
        if user == ctx.author:
            await ctx.respond("You cannot ban yourself.")
        elif user.top_role >= ctx.author.top_role:
            await ctx.respond("You cannot ban this user due to role hierarchy.")
        else:
            await user.ban()
            await ctx.respond(f"{user.mention} has been banned from the server.")
    else:
        await ctx.respond("You do not have permission to ban members.")

@bot.slash_command(name='mute', description='Mute a user in the server')
async def mute(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(name="Muted", reason="For muting users", permissions=discord.Permissions(send_messages=False, speak=False))
                
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)

            except discord.Forbidden:
                await ctx.respond("I do not have permissions to create roles. Please ask an administrator to create a role named 'Muted'.")
                return
            except discord.HTTPException:
                await ctx.respond("Failed to create the 'Muted' role. Please check server settings or try again later.")
                return
        
        if muted_role in user.roles:
            await ctx.respond(f"{user.mention} is already muted.")
        else:
            await user.add_roles(muted_role)
            await ctx.respond(f"{user.mention} has been muted.")
    else:
        await ctx.respond("You do not have permission to mute members.")

@bot.slash_command(name='unmute', description='Unmute a user in the server')
async def unmute(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.manage_roles:
        
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.respond("The 'Muted' role does not exist. Please create it first.")
            return
        
        if muted_role not in user.roles:
            await ctx.respond(f"{user.mention} is not muted.")
        else:
            await user.remove_roles(muted_role)
            await ctx.respond(f"{user.mention} has been unmuted.")
    else:
        await ctx.respond("You do not have permission to unmute members.")

@bot.slash_command(name='unban', description='Unban a user from the server')
async def unban(ctx, user: Option(str, description='User ID to unban')):
    if ctx.author.guild_permissions.ban_members:
        try:
            user_obj = await bot.fetch_user(user)
            await ctx.guild.unban(user_obj)
            await ctx.respond(f"{user_obj.mention} has been unbanned from the server.")
        except discord.NotFound:
            await ctx.respond("User not found. Please provide a valid User ID.")
    else:
        await ctx.respond("You do not have permission to unban members.")

@bot.slash_command(name='clear', description='Clear messages in a chat')
async def clear(ctx, amount_or_all: str):
    if amount_or_all.lower() == 'all':
        if ctx.author.guild_permissions.manage_messages:
            await ctx.channel.purge()
            await ctx.send("All messages have been deleted.", delete_after=5)
        else:
            await ctx.send("You do not have permission to delete messages.")
    else:
        try:
            amount = int(amount_or_all)
            if ctx.author.guild_permissions.manage_messages:
                await ctx.channel.purge(limit=amount)
                await ctx.send(f"{amount} messages have been deleted.", delete_after=5)
            else:
                await ctx.send("You do not have permission to delete messages.")
        except ValueError:
            await ctx.send("Invalid command usage. Please provide a number or 'all'.")

@bot.slash_command(name='trivia', description='Answer a random trivia question')
async def trivia(ctx):
    questions = [
        ("In what year did World War I begin?", "1914"),
        ("Who was the first President of the United States?", "George Washington"),
        ("In what year was the Berlin Wall torn down?", "1989"),
        ("Who was the pharaoh during the construction of the Great Pyramid of Giza?", "Khufu"),
        ("Who was the leader of the Soviet Union during World War II?", "Joseph Stalin"),

        ("What element is the main component of the Sun?", "Hydrogen"),
        ("Who developed the theory of relativity?", "Albert Einstein"),
        ("What gas makes up about 78% of the Earth's atmosphere?", "Nitrogen"),
        ("Who discovered penicillin?", "Alexander Fleming"),
        ("What is the hardest natural substance on Earth?", "Diamond"),

        ("What is the longest river in the world?", "Nile"),
        ("In which country is Mount Kilimanjaro located?", "Tanzania"),
        ("What city is the capital of Australia?", "Canberra"),
        ("What is the deepest lake in the world?", "Baikal"),
        ("In which country is Machu Picchu located?", "Peru"),

        ("Who wrote the novel 'War and Peace'?", "Leo Tolstoy"),
        ("Which novel begins with the line 'All happy families are alike...'?", "Anna Karenina"),
        ("Who is the author of 'Moby-Dick'?", "Herman Melville"),
        ("Who wrote the 'Odyssey'?", "Homer"),
        ("Which novel was written by George Orwell in 1949?", "1984"),

        ("Who composed Symphony No. 9 'Ode to Joy'?", "Ludwig van Beethoven"),
        ("Who painted 'Starry Night'?", "Vincent van Gogh"),
        ("Which work of Michelangelo is in the Sistine Chapel?", "The Creation of Adam"),
        ("Which famous Spanish painter created 'Guernica'?", "Pablo Picasso"),
        ("Which ballet by Pyotr Tchaikovsky is based on a story by E.T.A. Hoffmann?", "The Nutcracker"),

        ("What sport is considered the national sport of Japan?", "Sumo"),
        ("In what year were the first modern Olympic Games held?", "1896"),
        ("What is the name of the trophy awarded to the winner of the FIFA World Cup?", "FIFA World Cup Trophy"),
        ("What animal is the mascot for the 2024 Paris Olympics?", "Phrygian cap"),
        ("Who won the first Wimbledon tournament in 1877?", "Spencer Gore"),

        ("What is the fastest land animal?", "Cheetah"),
        ("Which fruit is known as the 'King of Fruits'?", "Durian"),
        ("What holiday is celebrated on December 25th?", "Christmas"),
        ("Which planet is the smallest in our solar system?", "Mercury"),
        ("What is the most popular pet in the world?", "Cat")

    ]
    
    question, answer = random.choice(questions)
    await ctx.respond(f"Trivia Question: {question}")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        return await ctx.send(f"Sorry, you took too long. The correct answer was {answer}.")

    if msg.content.lower() == answer.lower():
        await ctx.send("Correct! 🎉")
    else:
        await ctx.send(f"Wrong answer. The correct answer was {answer}.")

@bot.slash_command(name='guess', description='Guess a number between 1 and 100')
async def guess_number(ctx):
    number = random.randint(1, 100)
    await ctx.respond("I'm thinking of a number between 1 and 100. Can you guess what it is?")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    for attempt in range(5):
        try:
            msg = await bot.wait_for('message', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(f"Sorry, you took too long. The correct number was {number}.")

        guess = int(msg.content)
        
        if guess == number:
            return await ctx.send("Correct! 🎉 You guessed the number!")
        elif guess < number:
            await ctx.send("Too low! Try again.")
        else:
            await ctx.send("Too high! Try again.")

    await ctx.send(f"Sorry, you've used all your attempts. The correct number was {number}.")

class RPSButtonView(View):
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

@bot.slash_command(name='rps', description='Play Rock-Paper-Scissors')
async def rock_paper_scissors(ctx):
    view = RPSButtonView(ctx, None, None)
    await ctx.respond("Choose Rock, Paper, or Scissors:", view=view)
    
class TruthOrDareButtonView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=15)
        self.ctx = ctx
        self.result = None

    @discord.ui.button(label="Truth", style=discord.ButtonStyle.green)
    async def truth_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            if interaction.user != self.ctx.author:
                await interaction.followup.send("This is not your game!", ephemeral=True)
                return
            self.result = "truth"
            self.stop()
        except discord.errors.InteractionError:
            pass

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.red)
    async def dare_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            if interaction.user != self.ctx.author:
                await interaction.followup.send("This is not your game!", ephemeral=True)
                return
            self.result = "dare"
            self.stop()
        except discord.errors.InteractionError:
            pass


@bot.slash_command(name='truth_or_dare', description='Play a game of Truth or Dare')
async def truth_or_dare(ctx):
    truths = [
        "What is your biggest fear?",
        "What is the most embarrassing thing you've ever done?",
        "Have you ever lied to get out of trouble?",
        "What is your biggest regret?",
        "What is your secret talent?",
        "Have you ever had a crush on someone in this room?",
        "What is the worst gift you have ever received?",
        "What is the most childish thing you still do?",
        "Have you ever cheated on a test?",
        "What is the strangest dream you've ever had?",
        "If you could change one thing about your past, what would it be?",
        "Who is your secret crush?",
        "What is the most annoying habit you have?",
        "What is the worst lie you’ve ever told?",
        "What is something you have never told anyone?",
        "Who was your first kiss?",
        "What is the most embarrassing thing your parents have caught you doing?",
        "What is the biggest misconception about you?",
        "What is the most awkward date you have been on?",
        "Have you ever been in love?",
        "What is the weirdest thing you have ever done in public?",
        "What is your guilty pleasure?",
        "Have you ever stolen something?",
        "What is the most trouble you have been in?",
        "What is the weirdest food you have ever eaten?",
        "What is your biggest pet peeve?",
        "What is your biggest insecurity?",
        "What is the meanest thing you have ever said to someone?",
        "What is the most ridiculous thing you have done because you were bored?",
        "What is the best prank you have ever pulled?",
        "What is your most bizarre talent?",
        "Have you ever broken a bone?",
        "What is the most embarrassing song you secretly love?",
        "If you could swap lives with someone for a day, who would it be?"
    ]

    dares = [
        "Dance for 1 minute without music.",
        "Let someone write a word on your forehead with a marker.",
        "Sing the chorus of your favorite song.",
        "Do 20 pushups.",
        "Speak in an accent for the next 3 rounds.",
        "Try to lick your elbow.",
        "Post an embarrassing photo on social media.",
        "Imitate a celebrity until someone can guess who you are.",
        "Do your best chicken dance outside on the lawn.",
        "Let someone tickle you for 30 seconds.",
        "Talk in a funny voice for the next 5 minutes.",
        "Act like a monkey until your next turn.",
        "Do an impression of your favorite celebrity.",
        "Wear socks on your hands for the next 10 minutes.",
        "Dance with no music for 2 minutes.",
        "Do your best impression of a baby being born.",
        "Do your best impression of someone from the group.",
        "Do 20 jumping jacks.",
        "Let the person to your left draw on your face with a pen.",
        "Speak in a different accent until your next turn.",
        "Pretend to be a waiter/waitress and take snack orders from everyone in the group.",
        "Attempt to do a magic trick.",
        "Do your best breakdance move.",
        "Pretend to be a chicken for 1 minute.",
        "Let someone in the group give you a new hairstyle.",
        "Imitate a cartoon character.",
        "Do an impression of a celebrity of the group’s choosing.",
        "Try to juggle 3 items (none of which can be balls).",
        "Act like your favorite animal until your next turn.",
        "Pretend you are a ballerina until your next turn.",
        "Make a funny face and keep it that way until the next round.",
        "Try to touch your nose with your tongue.",
        "Let the group choose an item for you to brush your teeth with."
    ]

    view = TruthOrDareButtonView(ctx)
    await ctx.respond("Truth or Dare? Click a button to choose.", view=view)

    await view.wait()

    if view.result == "truth":
        truth = random.choice(truths)
        await ctx.send(f"Truth: {truth}")
    elif view.result == "dare":
        dare = random.choice(dares)
        await ctx.send(f"Dare: {dare}")
    else:
        await ctx.send("You didn't choose in time!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

class CasinoView(View):
    def __init__(self):
        super().__init__()
        self.add_item(BetButton())
        self.add_item(SpinButton())

class BetButton(Button):
    def __init__(self):
        super().__init__(label="Place Bet", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("You placed a bet! Now, spin the slot.", ephemeral=True)

class SpinButton(Button):
    def __init__(self):
        super().__init__(label="Spin", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        slots = ["🍒", "🍋", "🍊", "🍇", "🍉", "🍓"]
        result = [random.choice(slots) for _ in range(3)]
        if len(set(result)) == 1:
            await interaction.response.send_message(f"{' '.join(result)} - You won!", ephemeral=True)
        else:
            await interaction.response.send_message(f"{' '.join(result)} - You lost!", ephemeral=True)

@bot.slash_command(name='casino', description='Start a casino game')
async def casino(ctx):
    view = CasinoView()
    await ctx.respond("Welcome to the Casino! Place your bet and spin the slot machine.", view=view)

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
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
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToeView(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
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


@bot.slash_command(name='tic_tac_toe', description='Play a game of Tic-Tac-Toe')
async def tic_tac_toe(ctx):
    await ctx.respond("Tic Tac Toe: X goes first", view=TicTacToeView())

@bot.slash_command(name='would_you_rather', description='Play a game of Would You Rather')
async def would_you_rather(ctx):
    questions = [
        ("Would you rather be able to fly or be invisible?", "fly", "invisible"),
        ("Would you rather have more time or more money?", "time", "money"),
        ("Would you rather always be too hot or always be too cold?", "hot", "cold"),
        ("Would you rather be able to talk to animals or speak all foreign languages?", "animals", "languages"),
        ("Would you rather never be able to eat meat or never be able to eat vegetables?", "meat", "vegetables"),
        ("Would you rather lose your vision or your hearing?", "vision", "hearing"),
        ("Would you rather be famous or rich?", "famous", "rich")
    ]
    
    question, option1, option2 = random.choice(questions)

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
        self.board = ['🍎', '🍎', '🍌', '🍌', '🍒', '🍒', '🍇', '🍇', '🍉', '🍉', '🥭', '🥭', '🍓', '🍓', '🍍', '🍍', '🍊', '🍊', '🍋', '🍋']
        random.shuffle(self.board)
        self.first_selection = None
        self.matches = 0
        self.locked = False

        for i, label in enumerate(self.board):
            self.add_item(MemoryButton(label, i // 4, i % 5))

@bot.slash_command(name='memory_game', description='Play a memory game')
async def memory_game(ctx):
    await ctx.respond("Memory Game: Find all pairs!", view=MemoryGameView())

@bot.slash_command(name="giveaway", description="Starts a giveaway")
async def _giveaway(ctx, winners: int, prize: str):
    # Проверка на наличие прав администратора у пользователя
    if ctx.author.guild_permissions.administrator:
        guild = bot.get_guild(ctx.guild_id)
        
        # Получение всех участников сервера (исключая ботов)
        participants = [member for member in guild.members if not member.bot]

        # Проверка наличия участников
        if len(participants) == 0:
            await ctx.send("Not enough participants for the giveaway.")
            return

        # Выбор случайных победителей
        winners_list = random.sample(participants, min(winners, len(participants)))

        # Подготовка текста с победителями
        winners_text = "\n".join([winner.mention for winner in winners_list])
        win_message = f"Congratulations to the winners!\n{winners_text}"

        # Формирование Embed-сообщения с результатами розыгрыша
        embed = discord.Embed(title="🎉 Giveaway Results 🎉",
                              description=f"**Prize:** {prize}\n**Number of winners:** {winners}",
                              color=discord.Color.green())
        embed.add_field(name="Winners:", value=win_message)

        # Отправка Embed-сообщения с результатами розыгрыша
        await ctx.send(embed=embed)

    else:
        await ctx.send("You do not have permission to start a giveaway.")  # Сообщение об отсутствии прав администратора

timezones = {
    'UTC': 'UTC',
    'GMT': 'Etc/GMT',
    'CET': 'CET',
    'EET': 'EET',
    'IST': 'Asia/Kolkata',
    'CST': 'America/Chicago',
    'JST': 'Asia/Tokyo',
    'AEST': 'Australia/Sydney'
}

@bot.slash_command(name="time", description="Send time in different time zones")
async def time(ctx):
    time_message = "Current times in various timezones:\n"
    for zone, tz in timezones.items():
        timezone = pytz.timezone(tz)
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        time_message += f"{zone}: {current_time}\n"
    
    await ctx.send(time_message)
                
bot.run("")

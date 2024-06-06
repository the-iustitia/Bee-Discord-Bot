import discord
from discord.ext import commands
from discord import Option
import requests
from discord.ui import Button, View
import random
import asyncio

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

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

@bot.slash_command(name='ban', description='Ban a user from the server')
async def ban(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.ban_members:
        await user.ban()
        await ctx.respond(f"{user.mention} has been banned from the server.")
    else:
        await ctx.respond("You do not have permission to ban members.")

@bot.slash_command(name='mute', description='Mute a user in the server')
async def mute(ctx, user: Option(discord.Member, description='Select a user')):
    if ctx.author.guild_permissions.manage_roles:
        # Add your mute logic here, such as assigning a muted role to the user
        await ctx.respond(f"{user.mention} has been muted.")
    else:
        await ctx.respond("You do not have permission to mute members.")

@bot.command()
async def clear(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages have been deleted.", delete_after=5)
    else:
        await ctx.send("You do not have permission to delete messages.")

import random

@bot.slash_command(name='trivia', description='Answer a random trivia question')
async def trivia(ctx):
    questions = [
        ("What is the capital of France?", "Paris"),
        ("Who wrote 'Hamlet'?", "Shakespeare"),
        ("What is the largest planet in our solar system?", "Jupiter"),
        ("What year did the Titanic sink?", "1912"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci")
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
    
bot.run("")

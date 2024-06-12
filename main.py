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

@bot.slash_command(name='clear', description='Clear messages in a chat')
async def clear(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages have been deleted.", delete_after=5)
    else:
        await ctx.send("You do not have permission to delete messages.")

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

bot.run("MTI0NzEyNDQ5NDYzNjU1MjI5NA.Gm-yhE.XhSyEtyZmrqzu7N-cMWPPwLfz61F0NvEXtfVb0")

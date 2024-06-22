# Bee Discord Bot Documentation

## Description
This Discord bot offers users various games and features such as "Truth or Dare," "Casino," "Tic-Tac-Toe," "Would You Rather," "Memory Game," and giveaways. It can also provide the current time in different time zones.

## Commands

### `/truth_or_dare`
**Description:** Play a game of "Truth or Dare."

**Usage:** `/truth_or_dare`

**Details:** The user chooses between truth or dare by clicking the corresponding button. The bot then asks a question or gives a task from a predefined list.

### `/casino`
**Description:** Start a casino game.

**Usage:** `/casino`

**Details:** The user can place a bet and spin the slot machine by clicking the respective buttons. If three symbols match, the user wins.

### `/tic_tac_toe`
**Description:** Play a game of "Tic-Tac-Toe."

**Usage:** `/tic_tac_toe`

**Details:** Users play a game of Tic-Tac-Toe by taking turns clicking buttons on the game board. The game determines the winner or a tie.

### `/would_you_rather`
**Description:** Play a game of "Would You Rather."

**Usage:** `/would_you_rather`

**Details:** The bot asks the user a "Would You Rather" question, offering two options. The user chooses one of the options by clicking the corresponding button.

### `/memory_game`
**Description:** Play a memory game.

**Usage:** `/memory_game`

**Details:** The user finds pairs of matching symbols by revealing buttons on the game board. The game ends when all pairs are found.

### `/giveaway`
**Description:** Start a giveaway.

**Usage:** `/giveaway <winners> <prize>`

**Arguments:**
- `winners` (int): The number of winners.
- `prize` (str): The description of the prize.

**Details:** The server administrator can start a giveaway by specifying the number of winners and the prize description. The bot randomly selects winners from the server members.

### `/time`
**Description:** Send the current time in different time zones.

**Usage:** `/time`

**Details:** The bot sends the current time in various time zones such as UTC, GMT, CET, EET, IST, CST, JST, and AEST.

## Additional Information

### Classes and Functions

#### `TruthOrDareButtonView`
Class for creating an interface with buttons for selecting "Truth" or "Dare."

- **Methods:**
  - `truth_button`: Handler for clicking the "Truth" button.
  - `dare_button`: Handler for clicking the "Dare" button.

#### `CasinoView`
Class for creating the casino interface with "Place Bet" and "Spin" buttons.

#### `BetButton`
Class for the "Place Bet" button.

#### `SpinButton`
Class for the "Spin" button.

#### `TicTacToeButton`
Class for the Tic-Tac-Toe game board buttons.

#### `TicTacToeView`
Class for creating the Tic-Tac-Toe game interface.

- **Methods:**
  - `check_winner`: Checks for a winner on the game board.

#### `MemoryButton`
Class for the memory game board buttons.

#### `MemoryGameView`
Class for creating the memory game interface.

- **Methods:**
  - `callback`: Handler for button clicks to reveal symbols and check for matches.

### Notes
- Ensure you have the necessary permissions to use certain commands, such as `/giveaway`.
- The bot uses the `discord.py` library and `pytz` for working with Discord and time zones respectively.
- All commands must be registered with your bot before use.

This bot offers a variety of game features and can be extended with new commands and games as needed.

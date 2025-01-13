"""
Module with the definition of the constants used in the communication with the server.
"""

MSG_DELIMITER = ';'
"""The delimiter used to separate the parts of the messages sent between the server and the clients."""

MSG_TERMINATOR = '\n'
"""The terminator used to mark the end of the messages sent between the server and the clients."""

MSG_HEADER = 'IBGAME'
"""The header of the messages sent between the server and the clients."""

NUM_DELIMITER = ':'
"""The delimiter used to separate the numbers in parameters of the messages sent between the server and the clients."""

SEQ_DELIMITER = ','
"""The delimiter used to separate the sequences in parameters sent between the server and the clients."""

# 1 part messages

CMD_PING = 'PING'
"""The ping command."""

CMD_PONG = 'PONG'
"""The pong command."""

CMD_ACKW_VALID = 'SHAKE'
"""The shake command."""

CMD_CONFIRM_VALID = 'DEAL'
"""The deal command."""

CMD_LEAVE = 'LEAVE'
"""The leave command."""

CMD_CONFIRM_LEAVE = 'BYE'
"""The bye command."""

CMD_LOBBIES = 'LOBBIES'
"""The lobbies command."""

CMD_LOBBY = 'BRING_IT'
"""The lobby join request command."""

CMD_LOBBY_CREATE = 'CREATE'
"""The lobby create command."""

CMD_LOBBY_PAIRING = 'PAIRING'
"""The pairing command."""

CMD_LOBBY_PAIRED = 'PAIRED'
"""The paired command."""

CMD_READY = 'READY'
"""The ready command."""

CMD_GAME_WIN = 'WIN'
"""The win command."""

CMD_GAME_LOSE = 'LOST'
"""The lose command."""

CMD_WAIT = 'WAIT'
"""The wait command."""

CMD_WAITING = 'WAITING'
"""The waiting command."""

CMD_CONTINUE = 'CONTINUE'
"""The continue command."""

CMD_TKO = 'TKO'
"""The tko command."""

# 2 part messages

CMD_TRY_VALID = 'HAND'
"""The hand command."""

CMD_LOBBIES_RESP = 'LOBBIES'
"""The lobbies command."""

CMD_LOBBY_READY = 'PAIRED'
"""The paired command."""

CMD_PLAYER_TURN = 'TURN'
"""The turn command."""

CMD_TURN_ACTION = 'ACTION'
"""The action command."""

CMD_BOARD = 'BOARD'
"""The board command that represents the board of the player."""

# indices

PART_CMD_INDEX = 0
"""The index of the command in the messages sent between the server and the clients."""

PARAM_LOBBY_ID_INDEX = 0
"""The index of the lobby id in the messages sent between the server and the clients."""

PARAM_PLAYER_ID_INDEX = 0
"""The index of the player id in the messages sent between the server and the clients."""

PARAM_PLAYER_ON_TURN_INDEX = 0
"""The index of the player on turn in the messages sent between the server and the clients."""

PARAM_BOARD_INDEX = 0
"""The index of the board in the messages sent between the server and the clients."""

PARAM_CONTINUE_LOBBY_ID_INDEX = 0
"""The index of the lobby id in the continue command."""

PARAM_CONTINUE_OPPONENT_INDEX = 1
"""The index of the opponent in the continue command."""

PARAM_CONTINUE_PLAYER_ON_TURN_INDEX = 2
"""The index of the player on turn in the continue command."""

PARAM_CONTINUE_BOARD_INDEX = 3
"""The index of the board in the continue command."""

PART_BOARD_INDEX = 1
"""The index of the board in the messages sent between the server and the clients."""

PART_CONTINUE_LOBBY_ID_INDEX = 1
"""The index of the lobby id in the continue command."""

PART_CONTINUE_OPPONENT_INDEX = 2
"""The index of the opponent in the continue command."""

PART_CONTINUE_PLAYER_ON_TURN_INDEX = 3
"""The index of the player on turn in the continue command."""

PART_CONTINUE_BOARD_INDEX = 4
"""The index of the board in the continue command."""


# constants

PLAYER_NICKNAME_MAX_LENGTH = 20
"""The maximum length of the player's nickname."""

SERVER_ADDRESS_MAX_LENGTH = 18 # 9 IP, 5 port, 1 colon, 3 dots
"""The maximum length of the server address."""

SERVER_CONNECTION_TIMEOUT = 5
"""The timeout for the server connection in seconds."""

BOARD_SIDE_SIZE = 9
"""The size of the board side."""

BOARD_FREE_CELL = 0
"""The value of the free cell on the board."""

BOARD_PLAYER_CELL = 1
"""The value of the player cell on the board."""

BOARD_PLAYER_SHIP_LOST_CELL = -1
"""The value of the player ship lost cell on the board."""

BOARD_OPPONENT_SHIP_LOST_CELL = -2
"""The value of the opponent ship lost cell on the board."""

SCORE_SHIP_GAINED = 10
"""The score gained for a ship."""

SCORE_HIT = 20
"""The score gained for a hit."""

SCORE_LOST_SHIP = -10
"""The score lost for a lost ship."""

"""
Module with the definition of the constants used in the communication with the server.
"""

MSG_DELIMITER = ';'
"""The delimiter used to separate the parts of the messages sent between the server and the clients."""

MSG_TERMINATOR = '\n'
"""The terminator used to mark the end of the messages sent between the server and the clients."""

MSG_HEADER = 'IBGAME'
"""The header of the messages sent between the server and the clients."""

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

CMD_RES_MISS = 'MISS'
"""The miss command."""

CMD_RES_ACKW = 'ACTION_ACK'
"""The action_ack command."""

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

CMD_RES_HIT = 'HIT'
"""The hit command."""

CMD_RES_GAINED = 'GAIN'
"""The gain command."""

# indexes

CMD_INDEX = 0
"""The index of the command in the messages sent between the server and the clients."""

PARAM_LOBBY_ID_INDEX = 0
"""The index of the lobby id in the messages sent between the server and the clients."""

PARAM_PLAYER_ID_INDEX = 0
"""The index of the player id in the messages sent between the server and the clients."""
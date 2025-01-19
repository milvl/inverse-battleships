# Client files:

## File: client\src\main.py

### Functions/Methods

```python
def load_config(path: str) -> Dict:
    """
    Loads the configuration file from the given path.

    :param path: The path to the configuration file.
    :type path: str
    :return: The configuration file as a dictionary.
    :rtype: Dict
    """
```

```python
def main():
    """
    The main function of the client application.
    """
```

## File: client\src\const\typedefs.py

### Functions/Methods

```python
def __str__(self) -> str:
        """
        String representation of the class.

        :return: The string representation of the class.
        :rtype: str
        """
```

## File: client\src\game\connection_manager.py

### Functions/Methods

```python
def __str__(self) -> str:
        """
        Returns a string representation of the server response.

        :return: The string representation of the server response.
        :rtype: str
        """
```

```python
def __to_net_message(parts: List[str]) -> str:
        """
        Returns a formatted message from the parts for the network communication.

        :param parts: The parts of the message.
        :type parts: List[str]
        :return: The message.
        :rtype: str
        """
```

```python
def __from_net_message(message: str) -> List[str]:
        """
        Returns the parts of the message from the network communication.

        :param message: The message.
        :type message: str
        :return: The parts of the message.
        :rtype: List[str]
        """
```

```python
def __escape_net_message(message: str) -> str:
        """
        Escapes the message for network communication.

        :param message: The message to escape.
        :type message: str
        :return: The escaped message.
        :rtype: str
        """
```

```python
def __parse_parts(parts: List[str]) -> ServerResponse:
        """
        Parses the parts of a message from the server.

        :param parts: The parts of the message.
        :type parts: List[str]
        :return: The parsed message.
        :rtype: ServerResponse
        """
```

```python
def __init__(self, server_ip: str, server_port: int):
        """
        Initializes the connection manager.

        :param server_ip: The game server IP address.
        :type server_ip: str
        :param server_port: The game server port.
        :type server_port: int
        """
```

```python
def is_running(self) -> bool:
        """
        Checks if the connection manager is running and is connected to the server.

        :return: True if the connection manager is running and is connected to the server, false otherwise.
        :rtype: bool
        """
```

```python
def server_ip(self) -> str:
        """
        Getter for server_ip.

        :return: The game server IP address.
        :rtype: str
        """
```

```python
def port(self):
        """
        Getter for port.

        :return: The port of the game server.
        :rtype: int
        """
```

```python
def server_address(self):
        """
        Getter for server_address.

        :return: The game server address
        :rtype: str
        """
```

```python
def last_time_reply(self):
        """
        Getter for last_time_reply.

        :return: The time of the last reply from the server.
        :rtype: float
        """
```

```python
def start(self):
        """
        Connects to the server.
        """
```

```python
def __try_disconnect(self) -> bool:
        """
        Sends a disconnect message to the game server.

        :return: True if the disconnect message was sent successfully, false otherwise.
        :rtype: bool
        """
```

```python
def stop(self):
        """
        Disconnects from the server.
        """
```

```python
def __send_cmd(self, parts: List[str]):
        """
        Sends a command to the game server.

        :param parts: The parts of the command.
        :type parts: List[str]
        """
```

```python
def ping(self) -> bool:
        """
        Sends a ping message to the game server.

        :return: True if the ping message was sent and responded to successfully, false otherwise.
        :rtype: bool
        """
```

```python
def pong(self):
        """
        Sends a pong message to the game server.
        """
```

```python
def get_lobbies(self) -> List[str]:
        """
        Requests the list of lobbies from the game server.

        :return: The list of lobbies.
        :rtype: List[str]
        """
```

```python
def get_lobby(self) -> str:
        """
        Requests the lobby from the game server.

        :return: The lobby ID.
        :rtype: str
        """
```

```python
def join_lobby(self, lobby_id: str) -> str:
        """
        Joins a lobby with the given ID.

        :param lobby_id: The ID of the lobby to join.
        :type lobby_id: str
        :return: The lobby ID.
        :rtype: str
        """
```

```python
def check_for_players(self) -> str:
        """
        Checks for players in the lobby.

        :return: Opponent's username.
        :rtype: str
        """
```

```python
def game_ready(self) -> Tuple[List[List[int]], str, bool]:
        """
        Sends a ready message to the game server and receives current player's username,
        the board and the TKO flag if the player won dur to the opponent's connection 
        difficulties.

        :return: The username of the player whose turn it is, the board and TKO flag.
        :rtype: Tuple[List[List[int]], str, bool]
        """
```

```python
def send_action(self, action: Tuple[int, int]) -> str:
        """
        Sends an action to the game server.

        :param action: The action to send.
        :type action: Tuple[int, int]
        :return: The response from the server.
        :rtype: str
        """
```

```python
def wait_ackw(self):
        """
        Sends an acknowledgment to the server that the player is waiting for the opponent.
        """
```

```python
def __validate_connection(self) -> bool:
        """
        Authenticates the connection with the game server.
        It sends a handshake request to the server and waits for a response.
        Then, it validates the response and sends a confirmation message.

        :return: True if the connection was authenticated successfully, false otherwise.
        :rtype: bool
        """
```

```python
def __get_complete_message(self, message: str) -> Tuple[bool, str, str]:
        """
        Checks if the message is complete and returns the complete message and the tail of the message.

        :param message: The message.
        :type message: str
        :return: True if the message is complete, the complete message and the tail of the message.
        :rtype: Tuple[bool, str, str]
        """
```

```python
def receive_message(self) -> ServerResponse:
        """
        Receives a message from the game server.
        Is blocking until a message is received or an error occurs or timeout.

        :return: The received message.
        :rtype: ServerResponse
        """
```

```python
def __receive_command_response(self, expected_command: str, check_for_ping: bool = True) -> ServerResponse:
        """
        Receives a response from the game server and returns it if it matches the expected command.
        It also handles the case when the server sends a ping message before the expected response.

        :param expected_command: The expected command.
        :type expected_command: str
        :return: The received response.
        :rtype: ServerResponse
        """
```

```python
def login(self, username: str) -> bool:
        """
        Logs in to the game server with the given username.

        :param username: The username to log in with.
        :type username: str
        :return: True if the login was successful, false otherwise.
        :rtype: bool
        """
```

```python
def logout(self) -> bool:
        """
        Logs out from the game server.

        :return: True if the logout was successful, false otherwise.
        :rtype: bool
        """
```

## File: client\src\game\ib_game.py

### Functions/Methods

```python
def __proccess_input(events: PyGameEvents, key_input_validator: Callable = lambda y, x: x, self = None) -> Dict[str, Any]:
        """
        Processes the input events into a dictionary.
        Can return the following keys:
        - direction: The direction key pressed.
        - backspace: True if the backspace key was pressed.
        - return: True if the return key was pressed.
        - escape: True if the escape key was pressed.
        - new_char: The new character entered.
        - mouse_click: The position of the mouse click.
        - mouse_motion: The position of the mouse motion.

        :param events: PyGame events.
        :type events: PyGameEvents
        :param key_input_validator: Function to validate the keyboard input 
        and return a valid event.
        :type key_input_validator: Callable
        :param self: The IBGame object (if needed), defaults to None
        :type self: IBGame
        :return: The processed input events.
        :rtype: Dict[str, Any]
        """
```

```python
def __create_user_cfg(player_name: str, server_address: str = None):
        """
        Creates a new user configuration file.

        :param player_name: The name of the player.
        :type player_name: str
        """
```

```python
def __is_settings_input_valid(text_input):
        """
        Validates the server address input.

        :param text_input: The text input to validate.
        :type text_input: str
        :return: True if the input is valid, False otherwise.
        :rtype: bool
        """
```

```python
def __get_init_board(self):
        """
        Returns the initial board state.
        """
```

```python
def __init__(self, config: Dict[str, Any], assets: Dict[str, Any]):
        """
        Creates a new instance of the IBGame class.

        :param config: The configuration of the game.
        :type config: Dict[Any]
        :param assets: The assets of the game.
        :type assets: Dict[Any]
        """
```

```python
def start(self, window: pygame.Surface):
        """
        Initializes the game.

        :param window: The window of the game.
        :type window: pygame.Surface
        """
```

```python
def update_viewport_surfaces(self):
        """
        Updates the presentation surface.
        """
```

```python
def __get_debug_info_object(self):
        """
        Returns the debug info object. Used for debugging purposes.
        It is a pygame.Surface object with the debug info.

        :return: The debug info object.
        :rtype: pygame.Surface
        """
```

```python
def __get_pygame_events(self) -> PyGameEvents:
        """
        Returns the PyGame events.

        :return: The PyGame events.
        :rtype: PyGameEvents
        """
```

```python
def __set_up_user_session(self):
        """
        Prepares the data for the client session  
        based on user.
        """
```

```python
def __handle_window_resize(self, resize_event) -> bool:
        """
        Handles the window resize event.

        :param resize_event: The resize event.
        :type resize_event: pygame.event.Event
        :return: True if the debug info should be updated, False otherwise.
        """
```

```python
def __handle_context_resize(self):
        """
        Handles the context resize event.
        ### Changes the context so should be called with the graphics_lock \
        if the context handling is shared with net handler thread.
        """
```

```python
def __stop_net_handler_thread(self):
        """
        Stops the network handler thread.
        Will wait for the thread to finish.
        """
```

```python
def __append_game_session_async_updates(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends the game session async updates.

        :param inputs: The inputs.
        :type inputs: Dict[str, Any]
        :return: The updated inputs.
        :rtype: Dict[str, Any]
        """
```

```python
def __attempt_connection(self):
        """
        Attempts to connect to the server.
        """
```

```python
def __establish_connection(self):
        """
        Establishes the connection to the server.
        """
```

```python
def __retry_connection(self):
        """
        Retries the connection to the server.
        """
```

```python
def __transition_to_net_recovery(self, state_to_revert_to: int = None, connection_status_to_revert_to: int = None):
        """
        Transitions to the network recovery state. 
        ## WARNING: Uses the net_lock and graphics_lock.

        :param state_to_revert_to: The state to revert to. Defaults to None.
        :type state_to_revert_to: int, optional 
        :param connection_status_to_revert_to: The connection status to revert to. Defaults to None.
        :type connection_status_to_revert_to: int, optional
        """
```

```python
def __is_alive(self) -> bool:
        """
        Checks if the connection to the server is alive.
        """
```

```python
def __handle_net_connection_menu(self):
        """
        Handles basic server communication.
        """
```

```python
def __handle_net_basic_communication(self):
        """
        Handles basic server communication.
        """
```

```python
def __handle_net_get_lobbies(self):
        """
        Gets the list of lobbies from the server.
        """
```

```python
def __handle_net_get_lobby(self):
        """
        Gets the lobby info from the server.
        """
```

```python
def __handle_net_join_lobby(self):
        """
        Attempts to join the lobby.
        """
```

```python
def __handle_net_wait_for_players(self):
        """
        Waits for the players to join the lobby.
        """
```

```python
def __handle_net_game_ready(self):
        """
        Handles the game ready status.
        """
```

```python
def __handle_net_game_session(self):
        """
        Handles the game session connection updates.
        """
```

```python
def __prepare_init_state(self):
        """
        Prepares the initial state of the game.
        """
```

```python
def __prepare_main_menu(self):
        """
        Prepares the main menu state of the game.
        """
```

```python
def __prepare_settings_menu(self):
        """
        Prepares the settings menu state of the game.
        """
```

```python
def __prepare_connection_menu(self):
        """
        Prepares the connection menu state of the game.
        """
```

```python
def __prepare_lobby_selection(self):
        """
        Prepares the lobby selection state of the game.
        """
```

```python
def __prepare_lobby(self):
        """
        Prepares the lobby state of the game.
        """
```

```python
def __prepare_game_session(self):
        """
        Prepares the game session state of the game.
        """
```

```python
def __prepare_game_end_screen(self):
        """
        Prepares the game end screen state of the game.
        """
```

```python
def __prepare_net_recovery_screen(self):
        """
        Prepares the network recovery state of the game.
        """
```

```python
def __handle_update_feedback_init_state(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the INIT state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __handle_update_feedback_main_menu(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the MAIN_MENU state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        :raises ValueError: If an unknown option is selected.
        """
```

```python
def __handle_update_feedback_settings_menu(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the SETTINGS_MENU state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __handle_update_feedback_connection_menu(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the CONNECTION_MENU state.
        ### Can change context and usually runs with net handler thread (that can manipulate context) \
        so should be called with graphics_lock.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __handle_update_feedback_lobby_selection(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the LOBBY_SELECTION state.
        ### Can change context and usually runs with net handler thread (that can manipulate context) \
        so should be called with graphics_lock.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __handle_update_feedback_lobby(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the LOBBY state.
        ### Can change context and usually runs with net handler thread (that can manipulate context) \
        so should be called with graphics_lock.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __handle_update_feedback_game_session(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the GAME_SESSION state.
        ### Can change context and usually runs with net handler thread (that can manipulate context) \
        so should be called with graphics_lock.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __handle_update_feedback_net_recovery(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the NET_RECOVERY state.
        ### Can change context and usually runs with net handler thread (that can manipulate context) \
        so should be called with graphics_lock.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """
```

```python
def __update_init_state(self, events: PyGameEvents):
        """
        Handles the initialization state.
        
        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def connection_cleanup(self):
        """
        Cleans up all the resources related to the connection.
        """
```

```python
def __update_main_menu(self, events: PyGameEvents):
        """
        Handles the main menu state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_settings_menu(self, events: PyGameEvents):
        """
        Handles the settings menu state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_connection_menu(self, events: PyGameEvents):
        """
        Handles the connection menu state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_lobby(self, events: PyGameEvents):
        """
        Handles the lobby state. Lobby state represents the state when the player
        is either creating or joining a lobby.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_lobby_selection(self, events: PyGameEvents):
        """
        Handles the lobby selection state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_game_session(self, events: PyGameEvents):
        """
        Handles the game session state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_game_net_recovery(self, events: PyGameEvents):
        """
        Handles the network recovery state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def __update_game_end(self, events: PyGameEvents):
        """
        Handles the game end state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """
```

```python
def update(self) -> IBGameUpdateResult:
        """
        Updates the game state. This method should be called in the main loop 
        on each game tick. It uses priciples of state machine.

        :return: The update result.
        :rtype: IBGameUpdateResult
        """
```

## File: client\src\game\ib_game_state.py

### Functions/Methods

```python
def __init__(self):
        """
        Constructor method.
        """
```

```python
def state(self) -> int:
        """
        Represents the current state of the game.
        """
```

```python
def state(self, new_state: int):
        """
        Sets the state of the game.

        :param new_state: The new state of the game.
        :type new_state: int
        """
```

```python
def connection_status(self) -> int:
        """
        Represents the current connection status.
        """
```

```python
def connection_status(self, new_status: int):
        """
        Sets the connection status.

        :param new_status: The new connection status.
        :type new_status: int
        """
```

```python
def __str__(self) -> str:
        """
        Returns the name of the state.

        :return: The name of the state.
        :rtype: str
        """
```

## File: client\src\graphics\game_session.py

### Functions/Methods

```python
def __get_board_stats(board: List[List[int]]) -> Tuple[int, int, int, int]:
        """
        Gets the statistics of the board.

        :param board: The board.
        :type board: List[List[int]]
        :return: The statistics of the board.
        The statistics are as follows:
        - The number of free cells.
        - The number of player cells.
        - The number of player lost cells.
        - The number of opponent lost cells.
        :rtype: Tuple[int, int, int, int]
        """
```

```python
def __init__(self, 
                 surface: pygame.Surface, 
                 assets: IBAssets):
```

```python
def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the select menu.
        :rtype: pygame.Surface
        """
```

```python
def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """
```

```python
def last_score(self) -> int:
        """
        Getter for the last score property.

        :return: The last score.
        :rtype: int
        """
```

```python
def __get_score(self) -> int:
        """
        Gets the score of the game session.

        :return: The score.
        :rtype: int
        """
```

```python
def __get_panel(self, width: int, height: int) -> pygame.Surface:
        """
        Gets a panel for the game session.

        :param width: The width of the panel.
        :type width: int
        :param height: The height of the panel.
        :type height: int
        :return: The panel.
        :rtype: pygame.Surface
        """
```

```python
def __get_player_turn_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the player turn panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The player turn panel.
        :rtype: pygame.Surface
        """
```

```python
def __get_status_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the status panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The status panel.
        :rtype: pygame.Surface
        """
```

```python
def __get_last_action_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the last action panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The last action panel.
        :rtype: pygame.Surface
        """
```

```python
def __get_score_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the score panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The score panel.
        :rtype: pygame.Surface
        """
```

```python
def __get_info_panels(self, 
                          info_panel_width, 
                          info_panel_height, 
                          text_border_max_width, 
                          text_border_max_height) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface]:
        """
        Gets the info panels for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The info panels.
        :rtype: Tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface]
        """
```

```python
def __get_board(self, surface_width: int, surface_height: int) -> pygame.Surface:
        """
        Gets the board for the game session.

        :param surface_width: The width of the surface.
        :type surface_width: int
        :param surface_height: The height of the surface.
        :type surface_height: int
        :return: The board.
        :rtype: pygame.Surface
        """
```

```python
def __draw_objects(self) -> List[pygame.Rect]:
        """
        Draws the objects in the game session.

        :return: The rectangles of the objects.
        :rtype: List[pygame.Rect]
        """
```

```python
def draw(self) -> List[pygame.Rect]:
        """
        Draws the game session. Returns the 
        bounding rectangles of the objects drawn.

        :return: The select menu.
        :rtype: pygame.Surface
        """
```

```python
def redraw(self):
        """
        Redraws the game session. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """
```

```python
def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the game session.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """
```

## File: client\src\graphics\viewport.py

### Functions/Methods

```python
def __init__(self, surface: pygame.display):
        """
        Constructor for the Viewport class.

        :param surface: The surface to render the viewport to.
        :type surface: pygame.display
        """
```

```python
def draw(self) -> List[pygame.rect.Rect]:
        """
        Draws the viewport.

        :return: The rectangles that were updated.
        :rtype: List[pygame.rect.Rect]
        """
```

```python
def redraw(self):
        """
        Redraws the viewport.
        """
```

```python
def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the viewport state.

        :param events: The events to update the viewport with.
        :type events: Dict[str, Any]
        :return: The relevant updates.
        :rtype: Dict[str, Any]
        """
```

## File: client\src\util\assets_loader.py

### Functions/Methods

```python
def __load_colors(path: str) -> Dict:
        """
        Loads the colors from the given path.

        :param path: The path to the colors file.
        :type path: str
        :return: The colors as a dictionary.
        :rtype: Dict
        """
```

```python
def __load_text_resources(path: str) -> Dict:
        """
        Loads the text resources from the given path.

        :param path: The path to the text resources file.
        :type path: str
        :return: The text resources as a dictionary.
        :rtype: Dict
        """
```

```python
def __load_images(path: str) -> Dict:
        """
        Loads images from the given path.

        :param path: The path to the images directory.
        :type path: str
        :return: The images as a dictionary.
        :rtype: Dict
        """
```

```python
def __init__(self, resources_dir_path: str) -> None:
        """
        Constructor for the AssetsLoader class.

        :param resources_dir_path: The path to the resources directory.
        :type resources_dir_path: str
        """
```

```python
def load(self) -> Dict:
        """
        Loads all assets from the resources directory.

        :return: The assets as a dictionary.
        :rtype: Dict
        """
```

## File: client\src\util\etc.py

### Functions/Methods

```python
def maintains_min_window_size(width: int, height: int, min_width: int, min_height: int) -> bool:
    """
    Checks if the given width and height are greater than or equal to the given minimum width and height.

    :param width: The width.
    :type width: int
    :param height: The height.
    :type height: int
    :param min_width: The minimum width.
    :type min_width: int
    :param min_height: The minimum height.
    :type min_height: int
    :return: True if the width and height are greater than or equal to the minimum width and height, False otherwise.
    :rtype: bool
    """
```

```python
def get_scaled_resolution(width, height, ratio):
    """
    Calculate a scaled resolution based on the smaller dimension
    and a given aspect ratio as a float.

    :param width: The width.
    :type width: int
    :param height: The height.
    :type height: int
    :param ratio: The aspect ratio.
    :type ratio: float
    :return: The scaled width and height.
    :rtype: tuple
    """
```

```python
def hex_to_tuple(hex_str: str) -> tuple:
    """
    Converts a hexadecimal string to a tuple of integers.

    :param hex_str: The hexadecimal string.
    :type hex_str: str
    :return: The tuple of integers.
    :rtype: tuple
    """
```

## File: client\src\util\file.py

### Functions/Methods

```python
def load_json(path: str) -> Dict[str, Any]:
    """
    Loads the JSON file from the given path.

    :param path: The path to the JSON file.
    :type path: str
    :return: The JSON file as a dictionary.
    :rtype: Dict
    """
```

## File: client\src\util\generic_client.py

### Functions/Methods

```python
def __init__(self, host: str, port: int):
        """
        Creates a new ConnectionManager object.

        :param host: The host of the server.
        :type host: str
        :param port: The port of the server.
        :type port: int
        """
```

```python
def is_running(self):
        """
        Returns true if the client is running and is connected to the server, false otherwise.

        :return: True if the client is running and is connected to the server, false otherwise.
        :rtype: bool
        """
```

```python
def host(self):
        """
        Getter for host.

        :return: The host of the server.
        :rtype: str
        """
```

```python
def port(self):
        """
        Getter for port.

        :return: The port of the server.
        :rtype: int
        """
```

```python
def server_address(self):
        """
        Getter for server_address.

        :return: The server
        :rtype: str
        """
```

```python
def start(self):
        """
        Connects to the server.
        """
```

```python
def stop(self):
        """
        Disconnects from the server.
        """
```

```python
def __enter__(self):
        """
        Called when entering the context manager.
        """
```

```python
def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when exiting the context manager.
        """
```

```python
def send_message(self, message: str):
        """
        Sends a message to the server.

        :param message: The message.
        :type message: str
        :raises ConnectionError: If an error occurs while sending the message.
        :raises ValueError: If the message is too long to send.
        """
```

```python
def receive_expected_message(self, expected_message: str) -> bool:
    #     """
    #     Receives a message from the server and returns it if it matches the expected message.

    #     :param expected_message: The expected message.
    #     :type expected_message: str
    #     :return: True if the message matches the expected message, false otherwise.
    #     :rtype: bool
    #     :raises ConnectionError: If an error occurs while receiving the message
    #     """
```

```python
def receive_message(self) -> str:
        """
        Receives a message from the server.

        :return: The message.
        :rtype: str
        :raises ValueError: If no data is received.
        :raises ConnectionError: If an error occurs while receiving the message.
        """
```

## File: client\src\util\graphics.py

### Functions/Methods

```python
def get_rendered_text_with_size(text: str, width: int, height: int, font_path: str = None, color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
    """
    Renders the text with the given width and height limits.

    :param text: The text to render.
    :type text: str
    :param width: The width limit.
    :type width: int
    :param height: The height limit.
    :type height: int
    :param font_path: The path to the font to use for rendering, defaults to None
    :type font_path: str, optional
    :param color: The color to use for rendering, defaults to (255, 255, 255) (white)
    :type color: Tuple[int, int, int], optional
    :return: The rendered text.
    :rtype: pygame.Surface
    """
```

```python
def color_highlight(color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
    """
    Highlights the given color by increasing or decreasing its brightness.

    :param color: The color to highlight.
    :type color: Tuple[int, int, int]
    :return: The highlighted color.
    :rtype: Tuple[int, int, int]
    """
```

```python
def color_make_seethrough(color: Union[Tuple[int, int, int], Tuple[int, int, int, int]], alpha: int = 20) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
    """
    Makes the given color seethrough by adding an alpha value.

    :param color: The color to make seethrough.
    :type color: Tuple[int, int, int]
    :param alpha: The alpha value to add, defaults to 50
    :type alpha: int, optional
    :return: The seethrough color.
    :rtype: Tuple[int, int, int, int]
    """
```

```python
def debug_get_random_color() -> Tuple[int, int, int]:
    """
    Returns a random color.

    :return: A random color that is represented as a tuple of three integers.
    :rtype: Tuple[int, int, int]
    """
```

## File: client\src\util\init_setup.py

### Functions/Methods

## File: client\src\util\input_validators.py

### Functions/Methods

```python
def init_menu_key_input_validator(obj, key_event):
    """
    Validates the key input for the initial menu.

    :param key_event: The key event to validate.
    :type key_event: pygame.event.Event
    :return: The validated key event.
    :rtype: pygame.event.Event
    """
```

```python
def settings_key_input_validator(self, key_event):
    """
    Validates the key input for the settings menu.

    :param key_event: The key event to validate.
    :type key_event: pygame.event.Event
    :return: The validated key event.
    :rtype: pygame.event.Event
    """
```

## File: client\src\util\loggers.py

### Functions/Methods

```python
def __init__(self):
        """
        Does nothing.
        """
```

```python
def critical(self, *args):
        """
        Does nothing.
        """
```

```python
def exception(self, *args):
        """
        Does nothing.
        """
```

```python
def error(self, *args):
        """
        Does nothing.
        """
```

```python
def warning(self, *args):
        """
        Does nothing.
        """
```

```python
def warn(self, *args):
        """
        Does nothing.
        """
```

```python
def info(self, *args):
        """
        Does nothing.
        """
```

```python
def debug(self, *args):
        """
        Does nothing.
        """
```

```python
def format(self, record):
        """
        Formats the record with specified color (invalid defaults to white).
        
        :param record: The record
        :return: Formated record.
        """
```

```python
def __create_handler(handler_config: dict) -> logging.Handler:
    """
    Creates a handler for logger.

    :param handler_config: Handler config
    :return: Handler
    """
```

```python
def is_ready() -> bool:
    """
    Returns true if all loggers are ready, false otherwise.

    :return: True if all loggers are ready, false otherwise.
    """
```

```python
def set_path_to_config_file(json_file_path: str):
    """
    Sets up a path to the file with loggers config.

    :param json_file_path: Path to the file with loggers config
    """
```

```python
def get_logger(logger_name: str = '') -> logging.Logger:
    """
    Returns a logger configured from the config file.

    :param logger_name: Name of the logger
    :return: Logger
    """
```

```python
def get_temp_logger(name: str) -> logging.Logger|NullLogger:
    """
    Returns temp debug logger configured from the config file.

    :param name: Name of the temp logger
    :return: Temp logger
    """
```

## File: client\src\util\path.py

### Functions/Methods

```python
def get_project_root() -> str:
    """
    Gets the current working directory is the project root.

    :return: The project root path.
    :rtype: str
    """
```

```python
def is_valid_filename(filename: str) -> bool:
    """
    Check if the filename is valid.

    :param filename: The filename to check.
    :type filename: str
    :return: True if the filename is valid, False otherwise.
    :rtype: bool
    """
```

## File: client\src\graphics\menus\info_screen.py

### Functions/Methods

```python
def _draw_only_options(surface: pygame.Surface, 
                           options: List[MenuOption], 
                           assets: IBAssets, 
                           scale_option_rect_radius_to_surface_width: float = 0.1) -> List[pygame.Rect]:
        """
        Custom draw method for the InfoScreen that only draws the options.

        :param surface: The screen to draw the InfoScreen on.
        :type surface: pygame.Surface
        :param options: The options to draw.
        :type options: List[MenuOption]
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param scale_option_rect_radius_to_surface_width: The scale of the option rect radius to the surface width.
        :type scale_option_rect_radius_to_surface_width: float
        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """
```

```python
def __init__(self, surface: pygame.Surface, assets: IBAssets, info_text: str = ""):
        """
        Constructor method.

        :param surface: The screen to draw the InfoScreen on.
        :type surface: pygame.Surface
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param info_text: The text to show on the InfoScreen.
        :type info_text: str
        """
```

```python
def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the InfoScreen.

        :param events: The events that have occurred.
        :type events: Dict[str, Any]
        :return: The events that have occurred.
        :rtype: Dict[str, Any]
        """
```

## File: client\src\graphics\menus\input_menu.py

### Functions/Methods

```python
def __draw_content(obj):
        """
        Draws the content of the input menu.

        :param obj: The instance of the InputMenu class.
        :type obj: InputMenu
        """
```

```python
def _user_submitted(events: Dict[str, Any], submit_button_bounds: pygame.Rect):
        """
        Tests if the user has submitted the input.

        :param events: The events dictionary.
        :type events: Dict[str, Any]
        :param submit_button_bounds: The bounding rectangle of the submit button.
        :type submit_button_bounds: pygame.Rect
        :return: True if the user has submitted the input, False otherwise.
        :rtype: bool
        """
```

```python
def _handle_backspace(self):
        """
        Handles the backspace event.
        """
```

```python
def _handle_new_char(self, new_char: str):
        """
        Handles the new character event.

        :param new_char: The new character to handle.
        :type new_char: str
        """
```

```python
def __init__(self, 
                 surface: pygame.Surface, 
                 assets: IBAssets, 
                 label_text: str,
                 initial_text: str = ''):
        """
        Creates an instance of the InputMenu class.

        :param surface: The surface to render the input menu to.
        :type surface: pygame.Surface
        :param assets: The assets dictionary.
        :type assets: IBAssets
        :param label_text: The text of the input label.
        :type label_text: str
        :param initial_text: The initial text of the input field, defaults to ''.
        :type initial_text: str, optional
        """
```

```python
def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the input menu.
        :rtype: pygame.Surface
        """
```

```python
def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the input menu to.
        :type surface: pygame.Surface
        """
```

```python
def text_input(self):
        """
        Getter for the text_input property. Represents the 
        text input of the input menu without the cursor.

        :return: The text input of the input menu.
        :rtype: str
        """
```

```python
def redraw(self):
        """
        Redraws the input menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """
```

```python
def draw(self):
        """
        Draws the input menu (input label, input field, and submit button).

        :return: The bounding rectangle of the input menu.
        :rtype: pygame.Rect
        """
```

```python
def update(self, events: Dict[str, Any]):
        """
        Updates the input menu. Based on the events dictionary, the method
        returns a dictionary with keys 
        and values:
            - 'graphics_update' (bool): True if the graphics need to be updated,
            False otherwise.
            - 'submit' (bool): True if the user has submitted the input, False
            otherwise.

        :param events: The events dictionary.
        :type events: Dict[str, Any]
        :return: A dictionary with the keys 'graphics_update' and 'submit'.
        :rtype: Dict[str, Any]
        """
```

## File: client\src\graphics\menus\lobby_select.py

### Functions/Methods

```python
def __init__(self, surface: pygame.Surface, assets: IBAssets, lobbies: List[MenuOption] = None):
        """
        Constructor method.

        :param surface: The surface to draw the lobby select screen on.
        :type surface: pygame.Surface
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param lobbies: The lobbies to display.
        :type lobbies: List[MenuOption]
        """
```

```python
def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the select menu.
        :rtype: pygame.Surface
        """
```

```python
def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """
```

```python
def selected_lobby_name(self) -> str:
        """
        Getter for the selected lobby name.

        :return: The name of the selected lobby.
        :rtype: str
        """
```

```python
def __draw_objects(self):
        """
        Draws the objects on the lobby select screen.

        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """
```

```python
def draw(self):
        """
        Draws the select menu.

        :return: The select menu.
        :rtype: pygame.Surface
        """
```

```python
def redraw(self):
        """
        Redraws the select menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """
```

```python
def change_lobbies(self, lobbies: List[MenuOption], lobby_increment: int = 0):
        """
        Changes the lobbies displayed.

        :param lobbies: The new lobbies to display.
        :type lobbies: List[MenuOption]
        :param lobby_increment: The amount to increment the lobby index by.
        :type lobby_increment: int
        """
```

```python
def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the select menu.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """
```

## File: client\src\graphics\menus\primitives.py

### Functions/Methods

```python
def __init__(self, text: str):
        """
        Constructor for the MenuRectText class.
        
        :param text: The text of the object.
        :type text: str
        """
```

```python
def rect(self):
        """
        Getter for the rect property.

        :return: The rectangle of the text.
        :rtype: pygame.Rect
        """
```

```python
def render(self, 
               surface: pygame.display, 
               position: Tuple[int, int],
               height: int = DEFAULT_FONT_SIZE,
               width: int = DEFAULT_FONT_SIZE * 50,
               radius: int = -1,
               centered: bool = False,
               font_path: str = None, 
               color: Tuple[int, int, int] = DEFAULT_TEXT_COLOR,
               background_color: Union[Tuple[int, int, int], None] = None,
               outline_color: Union[Tuple[int, int, int], None] = None,
               text_align: int = TEXT_ALIGN_CENTER
               ) -> pygame.Rect:
        """
        Renders the text.
        Height is prefered because it is the implicit parameter for pygame.font.Font(None, height).

        :param surface: The surface to render the text to.
        :type surface: pygame.display
        :param position: The position to render the text at.
        :type position: tuple
        :param height: The height of the text, defaults to DEFAULT_FONT_SIZE
        :type height: int, optional
        :param width: The width of the text, defaults to DEFAULT_FONT_SIZE * 50
        :type width: int, optional
        :param radius: The radius of the rectangle, defaults to -1
        :type radius: int, optional
        :param centered: Whether to center the element, defaults to False
        :type centered: bool, optional
        :param font_path: The path to the font to use for rendering, defaults to None
        :type font_path: str, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: tuple, optional
        :param background_color: The background color to use for rendering, defaults to None
        :type background_color: tuple, optional
        :param outline_color: The outline color to use for rendering, defaults to None
        :type outline_color: tuple, optional
        :param text_align: The text alignment, defaults to TEXT_ALIGN_CENTER
        :type text_align: int, optional
        :return: The rectangle of the rendered text.
        :rtype: pygame.Rect
        """
```

```python
def __init__(self, text: str):
        """
        Constructor for the MenuTitle class.
        
        :param text: The text of the menu title.
        :type text: str
        """
```

```python
def __init__(self, text: str, highlighted: bool = False):
        """
        Constructor for the MenuOption class.
        
        :param text: The text of the menu option.
        :type text: str
        :param highlighted: Whether the menu option is highlighted, defaults to False
        :type highlighted: bool, optional
        """
```

```python
def text(self):
        """
        Getter for the text property.

        :return: The text of the menu option.
        :rtype: str
        """
```

```python
def highlighted(self):
        """
        Getter for the highlighted property.

        :return: Whether the menu option is highlighted.
        :rtype: bool
        """
```

```python
def highlighted(self, highlighted: bool):
        """
        Setter for the highlighted property.

        :param highlighted: Whether the menu option is highlighted.
        :type highlighted: bool
        """
```

```python
def render(self, 
               surface: pygame.Surface,
               position: 
               Tuple[int], 
               height: int = DEFAULT_FONT_SIZE, 
               width: int = DEFAULT_FONT_SIZE * 50, 
               radius: int = -1,
               centered: bool = False, 
               font_path: str = None, 
               color: Tuple[int] = DEFAULT_TEXT_COLOR, 
               background_color: Tuple[int] | None = None, 
               outline_color: Tuple[int] | None = None) -> pygame.Rect:
        """
        Renders the menu option.

        :param surface: The surface to render the menu option to.
        :type surface: pygame.Surface
        :param position: The position to render the menu option at.
        :type position: Tuple[int]
        :param height: The height of the menu option, defaults to DEFAULT_FONT_SIZE
        :type height: int, optional
        :param width: The width of the menu option, defaults to DEFAULT_FONT_SIZE * 50
        :type width: int, optional
        :param radius: The radius of the rectangle, defaults to -1 (90 degree corners)
        :type radius: int, optional
        :param centered: Whether to center the element, defaults to False
        :type centered: bool, optional
        :param font_path: The path to the font to use for rendering, defaults to None
        :type font_path: str, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: Tuple[int], optional
        :param background_color: The background color to use for rendering, defaults to None
        :type background_color: Tuple[int] | None, optional
        :param outline_color: The outline color to use for rendering, defaults to None
        :type outline_color: Tuple[int] | None, optional
        :return: The rectangle of the rendered menu option.
        :rtype: pygame.Rect
        """
```

```python
def __init__(self, text: str, is_focused: bool = False):
        """
        Constructor for the TextInput class.

        :param text: The text of the text input.
        :type text: str
        :param is_focused: Whether the text input is focused, defaults to False
        :type is_focused: bool, optional
        """
```

```python
def is_focused(self):
        """
        Getter for the is_focused property.

        :return: Whether the text input is focused.
        :rtype: bool
        """
```

```python
def is_focused(self, is_focused: bool):
        """
        Setter for the is_focused property.

        :param is_focused: Whether the text input is focused.
        :type is_focused: bool
        """
```

```python
def text(self):
        """
        Getter for the text property.

        :return: The text of the text input.
        :rtype: str
        """
```

```python
def text(self, text: str):
        """
        Setter for the text property.

        :param text: The text of the text input.
        :type text: str
        """
```

```python
def is_cursor_visible(self):
        """
        Getter for the is_cursor_visible property.

        :return: Whether the cursor is visible.
        :rtype: bool
        """
```

```python
def render(self, 
               surface: pygame.Surface, 
               position: Tuple[int], 
               height: int = DEFAULT_FONT_SIZE, 
               width: int = DEFAULT_FONT_SIZE * 50, 
               radius: int = -1, 
               centered: bool = False, 
               font_path: str = None, 
               color: Tuple[int] = DEFAULT_TEXT_COLOR, 
               background_color: Tuple[int] | None = None
               ) -> pygame.Rect:
        """
        Renders the text input.

        :param surface: The surface to render the text input to.
        :type surface: pygame.Surface
        :param position: The position to render the text input at.
        :type position: Tuple[int]
        :param height: The height of the text input, defaults to DEFAULT_FONT_SIZE
        :type height: int, optional
        :param width: The width of the text input, defaults to DEFAULT_FONT_SIZE * 50
        :type width: int, optional
        :param radius: The radius of the rectangle, defaults to -1 (90 degree corners)
        :type radius: int, optional
        :param centered: Whether to center the element, defaults to False
        :type centered: bool, optional
        :param font_path: The path to the font to use for rendering, defaults to None
        :type font_path: str, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: Tuple[int], optional
        :param background_color: The background color to use for rendering, defaults to None
        :type background_color: Tuple[int] | None, optional
        :return: The rectangle of the rendered text input.
        :rtype: pygame.Rect
        """
```

## File: client\src\graphics\menus\select_menu.py

### Functions/Methods

```python
def _draw_options(surface: pygame.Surface, 
                       options: List[MenuOption], 
                       top_offset: int, 
                       option_height: int, 
                       option_width: int, 
                       option_x: int, 
                       radius: int = -1,
                       color: Tuple[int, int, int] = _TEXT_COLOR,
                       background_color: Tuple[int, int, int] = _BACKGROUND_COLOR) -> List[pygame.Rect]:
        """
        Draws the options on the surface.

        :param surface: The surface to draw the options on.
        :type surface: pygame.Surface
        :param options: The options to draw.
        :type options: List[MenuOption]
        :param top_offset: The top offset of the options.
        :type top_offset: int
        :param option_height: The height of the options.
        :type option_height: int
        :param option_width: The width of the options.
        :type option_width: int
        :param option_x: The x-coordinate of the options.
        :type option_x: int
        :param radius: The radius of the options, default is -1.
        :type radius: int
        :param color: The color of the options, default is _TEXT_COLOR.
        :type color: Tuple[int, int, int]
        :param background_color: The background color of the options, default is _BACKGROUND_COLOR.
        :type background_color: Tuple[int, int, int]
        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """
```

```python
def __draw_title_and_options(surface: pygame.Surface, 
                                 title: MenuTitle, 
                                 options: List[MenuOption],
                                 scale_title_rect_radius_to_surface_width: float = 0.05, 
                                 scale_option_rect_radius_to_surface_width: float = 0.1,
                                 scale_title_area_to_screen_height: float = 0.35, 
                                 assets: IBAssets = None) -> List[pygame.Rect]:
        """
        Draws the title and options on the surface.

        :param surface: The surface to draw the title and options on.
        :type surface: pygame.Surface
        :param title: The title to draw.
        :type title: MenuTitle
        :param options: The options to draw.
        :type options: List[MenuOption]
        :param scale_title_rect_radius_to_surface_width: The scale of the title rectangle radius to the surface width, default is 0.05.
        :type scale_title_rect_radius_to_surface_width: float
        :param scale_option_rect_radius_to_surface_width: The scale of the option rectangle radius to the surface width, default is 0.1.
        :type scale_option_rect_radius_to_surface_width: float
        :param scale_title_area_to_screen_height: The scale of the title area to the screen height, default is 0.35.
        :type scale_title_area_to_screen_height: float
        :param assets: The assets of the game.
        :type assets: IBAssets
        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """
```

```python
def _draw_only_options(surface: pygame.Surface, options: List[MenuOption], assets: IBAssets, scale_option_rect_radius_to_surface_width: float = 0.1) -> List[pygame.Rect]:
        """
        Draws only the options on the surface.

        :param surface: The surface to draw the options on.
        :type surface: pygame.Surface
        :param options: The options to draw.
        :type options: List[MenuOption]
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param scale_option_rect_radius_to_surface_width: The scale of the option rectangle radius to the surface width, default is 0.1.
        :type scale_option_rect_radius_to_surface_width: float
        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """
```

```python
def __init__(self, surface: pygame.Surface, assets: IBAssets, title: MenuTitle = None, options: List[MenuOption] = None, scale_title_area_to_screen_height: float = 0.25):
        """
        Constructor method.

        :param surface: The screen to draw the select menu on.
        :type surface: pygame.Surface
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param title: The title of the select menu, default is None.
        :type title: MenuTitle
        :param options: The options of the select menu, default is None.
        :type options: List[MenuOption]
        :param scale_title_area_to_screen_height: The scale of the title area to the screen height, default is 0.25.
        :type scale_title_area_to_screen_height: float
        """
```

```python
def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the select menu.
        :rtype: pygame.Surface
        """
```

```python
def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """
```

```python
def selected_option_text(self):
        """
        Getter for the selected_option_text property.

        :return: The text of the selected option.
        :rtype: str
        """
```

```python
def highlighted_option_index(self):
        """
        Getter for the highlighted_option_index property.

        :return: The index of the highlighted option.
        :rtype: int
        """
```

```python
def set_highlighted_option_index(self, index: int):
        """
        Setter for the highlighted_option_index property.
        Keeps the index within the bounds of the options list.

        :param index: The index of the option to highlight.
        :type index: int
        """
```

```python
def unset_highlighted_option_index(self):
        """
        Unsets the highlighted option index.
        """
```

```python
def draw(self):
        """
        Draws the select menu.

        :return: The select menu.
        :rtype: pygame.Surface
        """
```

```python
def redraw(self):
        """
        Redraws the select menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """
```

```python
def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the select menu.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """
```

## File: client\src\graphics\menus\settings_menu.py

### Functions/Methods

```python
def __init__(self, surface: pygame.Surface, assets: IBAssets, label_text: str, server_address: str):
        """
        Initializes the settings menu.

        :param surface: The surface to draw the settings menu on.
        :type surface: pygame.Surface
        :param assets: The assets to use for the settings menu.
        :type assets: IBAssets
        :param label_text: The text to display as the label for the input field.
        :type label_text: str
        :param server_address: The server address to display in the input field.
        :type server_address: str
        """
```

```python
def redraw(self):
        """
        Redraws the input menu. Expects that the entire screen is redrawn with pygame.display.flip() after this method is called.
        """
```

```python
def draw(self) -> Rect:
        """
        Draws the input menu (input label, input field, and submit button).

        :return: The bounding rectangle of the input menu.
        :rtype: Rect
        """
```

```python
def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the settings menu based on the given events.

        :param events: The events to update the settings menu with.
        :type events: Dict[str, Any]
        :return: A dictionary containing the following
        :rtype: Dict[str, Any]
        """
```


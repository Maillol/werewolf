"""

Topics:

    com.werewolf.{game}.user.{user}.start_game    {"role": ""}

    com.werewolf.{game}.enter_in_phase.{phase}
    com.werewolf.{game}.role.{role}.enter_in_phase.{phase}    {"is_night": false,
                                                               "active": [],
                                                               "selectable": []}

    com.werewolf.{game}.
    com.werewolf.{game}.role.{role}.select_player    {"name": "", selected: 0}


    com.werewolf.{game}.close_phase                 {"killed": "" or null,
                                                     "resurrected": "" or null,
                                                     "winner": "" or null}
"""

import asyncio
from typing import Dict, List, Optional

import txaio
from autobahn.asyncio.component import Component
from autobahn.wamp.interfaces import ISession

from .models import Game, Notifier, Player

txaio.use_asyncio()
txaio.start_logging(level="debug")  # pylint: disable=no-member


class WampNotifier(Notifier):
    def __init__(self, session):
        self._session = session

    def send_to_players(self, game_name: str, players: List[Player],
                        subject: str, message):
        """
        Send message to player.
        """
        for player in players:
            self._session.publish(
                f"com.werewolf.{game_name}.user.{player.name}.{subject}",
                message)

    def send_to_game(self, game_name: str, subject: str, message):
        """
        Send message to all player of game.
        """
        self._session.publish(f"com.werewolf.{game_name}.{subject}", message)

    def send_to_role(self, game_name: str, role: str, subject: str, message):
        self._session.publish(
            f"com.werewolf.{game_name}.role.{role}.{subject}", message)


class Controller:
    def __init__(self, wamp_component: Component):
        self._wamp = wamp_component
        self._session: Optional[
            ISession] = None  # "None" while we're disconnected from WAMP router
        self._wamp.on("join", self._initialize)
        self._wamp.on("leave", self._uninitialize)
        self._games: Dict[str:Game] = {}
        self.log = txaio.make_logger()  # pylint:disable=no-member

    def _initialize(self, session: ISession, details):  # pylint: disable=unused-argument
        self._session = session
        session.register(self.create_game, "com.werewolf.create_game")
        session.register(self.join_game, "com.werewolf.join_game")
        session.register(self.start_game, "com.werewolf.start_game")
        session.register(self.select_player, "com.werewolf.select_player")
        session.register(self.player_listen_topic,
                         "com.werewolf.player_listen_topic")

    def _uninitialize(self, session, reason):  # pylint:disable=unused-argument
        self.log.error("Lost WAMP connection")
        self._session = None

    async def create_game(self, game_name, player_name):
        if game_name in self._games:
            raise Exception(f"The game with {game_name} already exist")

        game = Game(game_name, WampNotifier(self._session))
        player = Player(player_name)
        game.add_player(player)
        self._games[game_name] = game

    async def join_game(self, game_name, player_name):
        game = self._games[game_name]
        new_player = Player(player_name)
        return game.add_player(new_player)

    async def start_game(self, game_name):
        game = self._games[game_name]
        game.start()

        self.log.error("start game")
        future = asyncio.create_task(self._run_game(game))

        def log_game_error(game_task):
            exc = game_task.exception()
            if exc is not None:
                self.log.error(exc)
            del self._games[game_name]

        future.add_done_callback(log_game_error)

    async def player_listen_topic(self, game_name, player_name):
        game = self._games[game_name]
        game.player_listen_topic(player_name)

    async def _run_game(self, game):
        await game.wait_for_all_player_listen()
        while True:
            i = 0
            while not game.enter_in_next_phase():
                i += 1
                if i > 3:
                    raise RuntimeError("No next phase but game is not done.")

            await asyncio.sleep(30)
            if game.close_the_current_phase():
                break
            await asyncio.sleep(3)

    async def select_player(self, game_name, selected_player_name: str,
                            elector_player_name: str):
        game = self._games[game_name]
        return game.select_player_from_name(selected_player_name,
                                            elector_player_name)

import abc
from enum import Enum
from itertools import cycle
from random import shuffle
from typing import List, Iterable, Optional, Callable, Set
import asyncio


class Role(Enum):
    werewolf = 'werewolf'
    seer = 'seer'
    villager = 'villager'
    hunter = 'hunter'


class PlayerState(Enum):
    dead = 'dead'
    alive = 'alive'


class Player:
    name: str
    role: Optional[Role]
    state: PlayerState
    selected_by: Set['Player']

    def __str__(self):
        return f'<{self.name} {self.role.value} {self.state.value}>'

    def __init__(self, name: str):
        self.name = name
        self.role = None
        self.state = PlayerState.alive
        self.selected_by = set()

    @property
    def selected(self):
        return len(self.selected_by)

    def select(self, selected_by: str):
        if selected_by in self.selected_by:
            self.selected_by.remove(selected_by)
            return False
        else:
            self.selected_by.add(selected_by)
            return True

    def clear_selection(self):
        self.selected_by.clear()

    def to_dict(self, without=None):
        if without is None:
            without = ()
        dct = {}
        if 'name' not in without:
            dct['name'] = self.name
        if 'role' not in without:
            dct['role'] = None if self.role is None else self.role.value
        if 'state' not in without:
            dct['state'] = self.state.value
        if 'selected' not in without:
            dct['selected'] = self.selected
        return dct


class Notifier(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send_to_players(self,
                        game_name: str,
                        players: List[Player],
                        subject: str,
                        message):
        """
        Send message to player.
        """

    @abc.abstractmethod
    def send_to_game(self,
                     game_name: str,
                     subject: str,
                     message):
        """
        Send message to all player of game.
        """

    @abc.abstractmethod
    def send_to_role(self,
                     game_name: str,
                     role: str,
                     subject: str,
                     message):
        """
        Send message to all player with role.
        """


class Phase(metaclass=abc.ABCMeta):
    """
    A Phase of game.

    A Phase has 2 two mains methods `enter` and `close`.

    The `enter` method define which player is active or selectable setting
    the `active` attribute and `selectable` attribute.


    """
    role: Role
    is_night: bool = True
    text: str
    notifier: Notifier
    actives: List[Player]
    selectables: List[Player]

    def __init__(self, game_name: str, players: List[Player], notifier: Notifier):
        self.players: List[Player] = players
        self.notifier = notifier
        self.game_name = game_name
        self.actives = []
        self.selectables = []

    def _current_role_players(self):
        return [player
                for player in self.players
                if player.state is PlayerState.alive
                and player.role is self.role]

    def _other_role_player(self):
        return [player
                for player in self.players
                if player.state is PlayerState.alive
                and player.role is not self.role]

    def _kill_max_selected_player(self):
        player_to_kill = max(self.players, key=lambda p: p.selected)
        player_to_kill.state = PlayerState.dead
        for player in self.players:
            player.clear_selection()
        return player_to_kill

    @abc.abstractmethod
    def enter(self):
        """
        Set active and selectable player.
        """

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _notify_when_player_is_selected(self, player: Player):
        pass

    def select_player_from_name(self, selected: str, elector: str):
        if elector not in (player.name for player in self.actives):
            raise ValueError(f'Player {elector!r} cannot select an other player')

        for player in self.players:
            if player.name == selected:
                if player not in self.selectables:
                    raise ValueError(f'Player {selected!r} is not selectable')
                is_selected = player.select(elector)
                self._notify_when_player_is_selected(player)
                return is_selected
        raise ValueError(f'Player {selected!r} does not exist')

    def _close_msg(self, *, killed=None, resurrected=None):

        villager_alive = False
        werewolf_alive = False
        for player in self.players:
            if player.state is PlayerState.alive:
                if player.role is Role.werewolf:
                    werewolf_alive = True
                    if villager_alive:
                        winner = None
                        break
                elif player.role is Role.villager:
                    villager_alive = True
                    if werewolf_alive:
                        winner = None
                        break
        else:
            if villager_alive:
                winner = Role.villager.value
            else:
                winner = Role.werewolf.value

        return {
            'killed': killed,
            'resurrected': resurrected,
            'winner': winner}


class WerewolfPhase(Phase):
    role = Role.werewolf
    is_night = True

    def enter(self):
        self.actives = self._current_role_players()
        if not self.actives:
            return False
        self.selectables = self._other_role_player()

        self.notifier.send_to_game(
            self.game_name,
            f'enter_in_phase.{self.role.value}',
            {'is_night': self.is_night})
        self.notifier.send_to_role(
            self.game_name,
            self.role.value,
            f'enter_in_phase.{self.role.value}',
            {'active': [p.to_dict(without='role') for p in self.actives],
             'selectable': [p.to_dict(without='role') for p in self.selectables]})
        return True

    def close(self):
        removed_player = self._kill_max_selected_player()
        msg = self._close_msg(killed=removed_player.name)
        self.notifier.send_to_game(
            self.game_name,
            'close_phase.werewolf',
            msg)
        return msg['winner'] is not None

    def _notify_when_player_is_selected(self, player: Player):
        self.notifier.send_to_role(
            game_name=self.game_name,
            role=self.role.value,
            subject='select_player',
            message=player.to_dict(without='role'))


class SeerPhase(Phase):
    role = Role.seer
    is_night = True

    def close(self):
        selected_player = max(self.players, key=lambda p: p.selected)
        selected_player.clear_selection()
        if selected_player.state is PlayerState.dead:
            selected_player.state = PlayerState.alive
            msg = self._close_msg(resurrected=selected_player.name)
        else:
            selected_player.state = PlayerState.dead
            msg = self._close_msg(killed=selected_player.name)

        self.notifier.send_to_game(self.game_name, 'close_phase.seer', msg)
        return msg['winner'] is not None

    def enter(self):
        self.actives = self._current_role_players()
        if not self.actives:
            return False

        self.selectables = [p for p in self.players if p.role != self.role]
        self.notifier.send_to_game(
            self.game_name,
            f'enter_in_phase.{self.role.value}',
            {'is_night': self.is_night})
        self.notifier.send_to_role(
            self.game_name,
            self.role.value,
            f'enter_in_phase.{self.role.value}',
            {'active': [p.to_dict(without='role') for p in self.actives],
             'selectable': [p.to_dict(without='role') for p in self.selectables]})
        return True

    def _notify_when_player_is_selected(self, player: Player):
        self.notifier.send_to_role(
            game_name=self.game_name,
            role=self.role.value,
            subject='select_player',
            message=player.to_dict(without='role'))


class VillagerPhase(Phase):
    role = Role.villager
    is_night = False

    def close(self):
        removed_player = self._kill_max_selected_player()
        msg = self._close_msg(killed=removed_player.name)
        self.notifier.send_to_game(
            self.game_name,
            'close_phase.villager',
            msg)
        return msg['winner'] is not None

    def enter(self):
        all_player_alive = [p for p in self.players if p.state is PlayerState.alive]
        self.actives = all_player_alive
        if not self.actives:
            return False

        self.selectables = all_player_alive
        self.notifier.send_to_game(
            self.game_name,
            f'enter_in_phase.{self.role.value}',
            {'is_night': self.is_night,
             'active': [p.to_dict(without='role') for p in self.actives],
             'selectable': [p.to_dict(without='role') for p in self.selectables]})

        return True

    def _notify_when_player_is_selected(self, player: Player):
        self.notifier.send_to_game(
            game_name=self.game_name,
            subject='select_player',
            message=player.to_dict(without='role'))


def default_role_dispatcher(players: [List[Player]]):
    nb_werewolf = len(players) // 4
    if not nb_werewolf:
        nb_werewolf = 1

    roles_to_distribute = [Role.werewolf] * nb_werewolf
    roles_to_distribute.append(Role.seer)
    nb_villager = len(players) - len(roles_to_distribute)
    roles_to_distribute.extend([Role.villager] * nb_villager)
    shuffle(roles_to_distribute)
    for player, role in zip(players, roles_to_distribute):
        player.role = role


class Game:
    def __init__(
            self,
            name: str,
            notifier: Notifier,
            role_dispatcher: Callable[[List[Player]], None] = default_role_dispatcher):
        self.name = name
        self.notifier = notifier
        self.role_dispatcher = role_dispatcher
        self._players: List[Player] = []
        self._phases: Iterable[Phase] = cycle((
            WerewolfPhase(self.name, self._players, notifier),
            SeerPhase(self.name, self._players, notifier),
            VillagerPhase(self.name, self._players, notifier)))

        self._current_phase: Optional[Phase] = None
        self._not_listening_players = set()
        self._all_player_listen = asyncio.Event()

    def add_player(self, player: Player):
        self._players.append(player)
        self._not_listening_players.add(player.name)
        msg = [player.to_dict(without='role') for player in self._players]
        self.notifier.send_to_game(
            game_name=self.name,
            subject='add_player',
            message=msg)
        return msg

    def get_players(self):
        return (player for player in self._players)

    def start(self):
        self.role_dispatcher(self._players)
        for player in self._players:
            self.notifier.send_to_players(
                self.name,
                [player],
                'start_game',
                player.to_dict())

    def player_listen_topic(self, player_name):
        self._not_listening_players.remove(player_name)
        if not self._not_listening_players:
            self._all_player_listen.set()

    async def wait_for_all_player_listen(self):
        await self._all_player_listen.wait()

    def enter_in_next_phase(self):
        self._current_phase = next(self._phases)
        return self._current_phase.enter()

    def close_the_current_phase(self):
        return self._current_phase.close()

    def select_player_from_name(self, selected: str, elector: str):
        self._current_phase.select_player_from_name(selected, elector)

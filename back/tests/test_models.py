import pprint
from unittest import TestCase

from werewolf.models import Game, Notifier, Player, Role


class FakeNotifier(Notifier):

    def __init__(self):
        self.messages_sent = []

    def send_to_players(self,
                        game_name,
                        players,
                        subject,
                        message):
        """
        Send message to player.
        """
        for player in players:
            self.messages_sent.append((f'{game_name}.{player.name}.{subject}', message))

    def send_to_game(self,
                     game_name,
                     subject,
                     message):
        """
        Send message to all player of game.
        """
        self.messages_sent.append((f'{game_name}.{subject}', message))

    def send_to_role(self,
                     game_name,
                     role,
                     subject,
                     message):
        self.messages_sent.append((f'{game_name}.{role}.{subject}', message))

    def assert_message_sent(self, topic, expected_msg):
        if any(msg == (topic, expected_msg) for msg in self.messages_sent):
            return
        raise AssertionError(
            f"No message {expected_msg} sent to {topic} found in:\n{pprint.pformat(self.messages_sent, width=1)}")

    def reset(self):
        del self.messages_sent[:]


class BaseTestGame(TestCase):

    def setUp(self):
        def role_dispatcher(players):
            for p, r in zip(players, (Role.villager, Role.seer, Role.werewolf, Role.villager)):
                p.role = r

        self.notifier = FakeNotifier()
        self.game = Game(
            name='part',
            notifier=self.notifier,
            role_dispatcher=role_dispatcher)

        self.players = {
            'Tom': Player(name='Tom'),
            'Lea': Player(name='Lea'),
            'Bob': Player(name='Bob'),
            'Isa': Player(name='Isa')}

        self.game.add_player(self.players['Tom'])
        self.game.add_player(self.players['Lea'])
        self.game.add_player(self.players['Bob'])
        self.game.add_player(self.players['Isa'])


class TestGameStart(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()

    def test_player_tom_sould_be_villager(self):
        self.assertIs(self.players['Tom'].role, Role.villager)

    def test_player_lea_sould_be_seer(self):
        self.assertIs(self.players['Lea'].role, Role.seer)

    def test_player_bob_sould_be_werewolf(self):
        self.assertIs(self.players['Bob'].role, Role.werewolf)

    def test_player_isa_sould_be_werewolf(self):
        self.assertIs(self.players['Isa'].role, Role.villager)

    def test_player_tom_sould_be_notify_with_role_villager(self):
        expected = {'name': 'Tom',
                    'role': 'villager',
                    'selected': 0,
                    'state': 'alive'}
        self.notifier.assert_message_sent(
            'part.Tom.start_game', expected)

    def test_player_lea_sould_be_notify_with_role_seer(self):
        expected = {'name': 'Lea',
                    'role': 'seer',
                    'selected': 0,
                    'state': 'alive'}
        self.notifier.assert_message_sent(
            'part.Lea.start_game', expected)

    def test_player_bob_sould_be_notify_with_role_werewolf(self):
        expected = {'name': 'Bob',
                    'role': 'werewolf',
                    'selected': 0,
                    'state': 'alive'}
        self.notifier.assert_message_sent(
            'part.Bob.start_game', expected)

    def test_player_isa_sould_be_notify_with_role_villager(self):
        expected = {'name': 'Isa',
                    'role': 'villager',
                    'selected': 0,
                    'state': 'alive'}
        self.notifier.assert_message_sent(
            'part.Isa.start_game', expected)


class TestEnterInWerewolfPhaseGame(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()
        self.notifier.reset()
        self.game.enter_in_next_phase()

    def test_player_bob_should_be_received(self):
        self.notifier.assert_message_sent(
            'part.werewolf.enter_in_phase.werewolf',
            {'active': [{'name': 'Bob',
                         'selected': 0,
                         'state': 'alive'}],
             'selectable': [{'name': 'Tom',
                             'selected': 0,
                             'state': 'alive'},
                            {'name': 'Lea',
                             'selected': 0,
                             'state': 'alive'},
                            {'name': 'Isa',
                             'selected': 0,
                             'state': 'alive'}]})

    def test_all_player_should_be_received_enter_in_phase_werewolf(self):
        self.notifier.assert_message_sent(
            'part.enter_in_phase.werewolf',
            {'is_night': True})


class TestCloseInWerewolfPhaseGame(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Tom', 'Bob')
        self.notifier.reset()
        self.game.close_the_current_phase()

    def test_all_player_should_receive_tom_is_killed_notification(self):
        self.notifier.assert_message_sent(
            'part.close_phase.werewolf',
            {'killed': 'Tom',
             'resurrected': None,
             'winner': None})


class TestEnterInSeerPhaseGame(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Tom', 'Bob')
        self.game.close_the_current_phase()
        self.notifier.reset()
        self.game.enter_in_next_phase()

    def test_all_player_should_receive_enter_in_phase_seer_notification(self):
        self.notifier.assert_message_sent(
            'part.enter_in_phase.seer', {'is_night': True})

    def test_lea_should_receive_a_notification(self):
        self.notifier.assert_message_sent(
            'part.seer.enter_in_phase.seer',
            {'active': [{'name': 'Lea',
                         'selected': 0,
                         'state': 'alive'}],
             'selectable': [{'name': 'Tom',
                             'selected': 0,
                             'state': 'dead'},
                            {'name': 'Bob',
                             'selected': 0,
                             'state': 'alive'},
                            {'name': 'Isa',
                             'selected': 0,
                             'state': 'alive'}]})


class TestCloseSeerPhaseGameResurrectingTom(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Tom', 'Bob')
        self.game.close_the_current_phase()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Tom', 'Lea')
        self.notifier.reset()
        self.game.close_the_current_phase()

    def test_all_player_should_receive_close_phase_seer_notification(self):
        self.notifier.assert_message_sent(
            'part.close_phase.seer',
            {'killed': None,
             'resurrected': 'Tom',
             'winner': None})


class TestCloseSeerPhaseGameKillingBob(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Tom', 'Bob')
        self.game.close_the_current_phase()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Bob', 'Lea')
        self.notifier.reset()
        self.game.close_the_current_phase()

    def test_all_player_should_receive_close_phase_seer_notification(self):
        self.notifier.assert_message_sent(
            'part.close_phase.seer',
            {'killed': 'Bob',
             'resurrected': None,
             'winner': 'villager'})


class TestCloseSeerPhaseGameKillingIsa(BaseTestGame):

    def setUp(self):
        super().setUp()
        self.game.start()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Tom', 'Bob')
        self.game.close_the_current_phase()
        self.game.enter_in_next_phase()
        self.game.select_player_from_name('Isa', 'Lea')
        self.notifier.reset()
        self.game.close_the_current_phase()

    def test_all_player_should_receive_close_phase_seer_notification(self):
        self.notifier.assert_message_sent(
            'part.close_phase.seer',
            {'killed': 'Isa',
             'resurrected': None,
             'winner': 'werewolf'})

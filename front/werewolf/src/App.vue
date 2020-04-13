<template>
  <div id="app">
    {{ message }}

    <join-or-create
        v-if="displayLoginPage"
        v-on:create-game="createGame"
        v-on:join-game="joinGame"
    ></join-or-create>
    <div
        v-if="displayStartGameButton">
            <button v-on:click="startGame">Start</button>
    </div>
    <ol>
        <player-item
            v-for="player in players"
            v-bind:player="player"
            v-bind:key="player.name"
            v-on:player-clicked="selectPlayer(player.name)"
        ></player-item>
    </ol>
  </div>
</template>

<script>
import Vue from 'vue'
import autobahn from 'autobahn'
import when from 'when'

import JoinOrCreate from './components/JoinOrCreate.vue'
import PlayerItem from './components/PlayerItem.vue'

var onSubscribeWithSuccess = function (sub) {
    console.log('subscribed to topic', sub.topic);
};

var onSubscribeWithError = function (error) {
    console.log('failed to subscribe to topic', error);
};

export default {
  name: 'App',
  components: {
    JoinOrCreate,
    PlayerItem
  },
  data: function () {
      return {
          message: 'Connecting ...',
          playerName: '',
          playerRole: '',
          gameName: '',
          players: [],
          displayLoginPage: true,
          displayStartGameButton: false,
          is_night: false,
          select_player: [],
          active_player: [],
      }
  },
  mounted() {
    var app = this;

    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:8081/ws',
        realm: 'realm1'
    });

    var promise = when.promise(function(resolve) {
        connection.onopen = function (session) {
            console.log('Connected to crossbar');
            app.message = '';
            resolve(session);
        };
        connection.open();
    });

    promise.then(
        function(session) {
            app.session = session;

            var onAnyEvent = function(args, kwargs, details) {
                console.log('Event received on', details.topic, args, kwargs);
            };

            session.subscribe('com.werewolf', onAnyEvent, {match: 'prefix'}).then(
               function (sub) {
                  console.log('subscribed to topic', sub.topic);
               },
               function (error) {
                  console.log('failed to subscribe to topic', error);
               }
            );
        },
        function(error) {
            console.log('failed to open session', error);
        }
    );
  },
  methods: {
    createGame(gameName, playerName) {
        this.gameName = gameName;
        this.playerName = playerName;
        this.message = 'Create ' + this.gameName + ' ' + this.playerName;
        var self = this;
        this.session.call('com.werewolf.create_game', [this.gameName, this.playerName]).then(
            function (result) {
                console.log(result);  // TODO remove it.
                self.subscribeToTopic();
                self.subscribeToTopicWithUser();
                self.displayStartGameButton = true;
                self.displayLoginPage = false;
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    joinGame(gameName, playerName) {
        this.gameName = gameName;
        this.playerName = playerName;
        this.message = 'Join ' + this.gameName + ' ' + this.playerName;
        var self = this;
        this.session.call('com.werewolf.join_game', [this.gameName, this.playerName]).then(
            function (result) {
                self.subscribeToTopic();
                self.subscribeToTopicWithUser();
                self.message = 'Vous avez rejoin la parti';
                self.players = result;
                self.displayLoginPage = false;
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    startGame() {
        var self = this;
        this.session.call('com.werewolf.start_game', [this.gameName]).then(
            function (result) {
                console.log(result);  // TODO remove it.
                self.displayStartGameButton = false;
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    subscribeToTopicWithRole() {
        var prefix = `com.werewolf.${this.gameName}.role.${this.playerRole}`;
        this.session.subscribe(`${prefix}.enter_in_phase`, this.onEnterInPhase, {match: "prefix"}).then(onSubscribeWithSuccess, onSubscribeWithError);
        this.session.subscribe(`${prefix}.select_player`, this.onSelectedPlayer).then(onSubscribeWithSuccess, onSubscribeWithError);
    },
    subscribeToTopicWithUser() {
        this.session.subscribe(`com.werewolf.${this.gameName}.user.${this.playerName}.start_game`,
                               this.onPlayerStartGame).then(onSubscribeWithSuccess, onSubscribeWithError);
    },
    subscribeToTopic() {
        var prefix = `com.werewolf.${this.gameName}`;
        this.session.subscribe(`${prefix}.enter_in_phase`,
                               this.onEnterInPhase,
                               {match: "prefix"}).then(onSubscribeWithSuccess, onSubscribeWithError);

        this.session.subscribe(`${prefix}.select_player`,
                               this.onSelectedPlayer).then(onSubscribeWithSuccess, onSubscribeWithError);

        this.session.subscribe(`${prefix}.close_phase`,
                               this.onClosePhase,
                               {match: "prefix"}).then(onSubscribeWithSuccess, onSubscribeWithError);
        this.session.subscribe(`${prefix}.add_player`,
                               this.onPlayerJoin).then(onSubscribeWithSuccess, onSubscribeWithError);
    },
    selectPlayer(selectPlayer) {
        console.log('selectPlayer', selectPlayer);
        this.session.call('com.werewolf.select_player', [this.gameName, selectPlayer, this.playerName]).then(
            function (result) {
                console.log('result');
                if (result) {
                    console.log('player selected !');
                } else {
                    console.log('player not selected !');
                }
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    updatePlayer(playerName, key, value) {
        var index = this.players.findIndex((element) => element.name === playerName);
        console.log('updatePlayer', playerName, this.players);
        Vue.set(this.players[index], key, value);
    },
    onEnterInPhase(args, kwargs, details) {
        var phase = details.topic.substring(details.topic.lastIndexOf('.') + 1);
        if (args[0].is_night !== undefined) {
            this.message = `Entrer dans la phase ${phase}`;
        }
        if (args[0].selectable !== undefined) {
            if (this.playerRole === phase) {
                args[0].selectable.forEach((player) => this.updatePlayer(player.name, 'selectable', true));
            }
        }
        if (args[0].active !== undefined) {
            console.log('onEnterInPhase active', args[0]);
        }
    },
    onClosePhase(args, kwargs, details) {
        var phase = details.topic.substring(details.topic.lastIndexOf('.') + 1);
        console.log('close phase', phase, args, kwargs, details);
        var killed = args[0].killed;
        var resurrect = args[0].resurrect;
        var winner = args[0].winner;

        if (killed) {
            this.updatePlayer(killed, 'state', 'dead');
            this.message = `${killed} a été tué`;
        }

        if (resurrect) {
            this.updatePlayer(resurrect, 'state', 'dead');
            this.message = `${resurrect} a été ressuscité`;
        }

        if (winner) {
            this.message = `${winner} ont gagnés`;
        }
        this.players.forEach((player) => this.updatePlayer(player.name, 'selectable', false));
    },
    onPlayerJoin(args, kwargs, details) {
        console.log(kwargs, details);  // TODO remove it.
        this.players = args[0];
    },
    onPlayerStartGame(args, kwargs, details) {
        console.log(kwargs, details);  // TODO remove it.
        this.playerRole = args[0].role;
        this.updatePlayer(this.playerName, 'role', this.playerRole);
        this.subscribeToTopicWithRole();
        this.session.call('com.werewolf.player_listen_topic', [this.gameName, this.playerName]).then(
            function (result) {
                console.log(result);  // TODO remove it.
                console.log('RPC com.werewolf.player_listen_topic OK');
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    onSelectedPlayer(args, kwargs, details) {
        console.log(kwargs, details);  // TODO remove it.
        var select_player = args[0];
        var index = this.players.findIndex((element) => element.name === select_player.name);
        Vue.set(this.players, index, select_player);
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

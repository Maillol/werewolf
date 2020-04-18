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
    <div>
        <player-board
            v-bind:players="players"
            v-bind:selectPlayer="selectPlayer"
        ></player-board>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import API from './API/index.js'

import JoinOrCreate from './components/JoinOrCreate.vue'
import PlayerBoard from './components/PlayerBoard.vue'


export default {
  name: 'App',
  components: {
    JoinOrCreate,
    PlayerBoard
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
    var api = new API('ws://127.0.0.1:8081/ws', 'realm1');
    api.onSelectedPlayer = this.onSelectedPlayer;
    api.onEnterInPhase = this.onEnterInPhase;
    api.onRoleAffected = this.onRoleAffected;
    api.onPlayerSelectable = this.onPlayerSelectable;
    api.onPlayerJoin = this.onPlayerJoin;
    api.onClosePhase = this.onClosePhase;
    var self = this;
    api.connect().then(
        function (result) {
            self.message = '';
            return result;
        },
        function (error) {
            self.message = 'ERROR: ' + error.args[0];
        }
    );
    this.api = api;
  },
  methods: {
    createGame(gameName, playerName) {
        this.gameName = gameName;
        this.playerName = playerName;
        this.message = 'Create ' + this.gameName + ' ' + this.playerName;
        var self = this;
        this.api.createGame(this.gameName, this.playerName).then(
            function (result) {
                self.displayStartGameButton = true;
                self.displayLoginPage = false;
                return result;
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
        this.api.joinGame(this.gameName, this.playerName).then(
            function (result) {
                self.message = `Vous avez rejoin la parti this.gameName`;
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
        this.api.startGame(this.gameName).then(
            function (result) {
                self.displayStartGameButton = false;
                return result;
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    selectPlayer(selectPlayer) {
        this.api.selectPlayer(this.gameName, selectPlayer, this.playerName).then(
            function (result) {
                if (result) {
                    console.log('player selected !');
                } else {
                    console.log('player not selected !');
                }
                return result;
            },
            function (error) {
                self.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    updatePlayer(playerName, key, value) {
        var index = this.players.findIndex((element) => element.name === playerName);
        Vue.set(this.players[index], key, value);
    },
    onEnterInPhase(phase) {
        var phaseName = phase.phase;
        self.message = `Entrée dans la phase ${phaseName}`;
    },
    onClosePhase(phaseDone) {
        var killed = phaseDone.killed;
        var resurrect = phaseDone.resurrect;
        var winner = phaseDone.winner;

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
        this.players.forEach((player) => this.updatePlayer(player.name, 'selected', 0));
    },
    onPlayerJoin(players) {
        this.players = players;
    },
    onRoleAffected(role) {
        this.playerRole = role;
        this.updatePlayer(this.playerName, 'role', role);
    },
    onSelectedPlayer(selectedPlayer) {
        var index = this.players.findIndex((element) => element.name === selectedPlayer.name);
        Vue.set(this.players, index, selectedPlayer);
    },
    onPlayerSelectable(selectable, active) {
        console.log(selectable, active);
        selectable.forEach((player) => this.updatePlayer(player.name, 'selectable', true));
    }
  }
}
</script>


<style lang="scss">
  @import "../node_modules/knacss/sass/knacss.scss";
</style>

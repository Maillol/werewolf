<template>
  <div id="app">
    <div v-bind:class="{ alert: !isNight, 'alert--inverse': isNight }">{{ message }}</div>
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
          isNight: true,
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
    var that = this;
    api.connect().then(
        function (result) {
            that.message = '';
            return result;
        },
        function (error) {
            that.message = 'ERROR: ' + error.args[0];
        }
    );
    this.api = api;
  },
  methods: {
    createGame(gameName, playerName) {
        this.gameName = gameName;
        this.playerName = playerName;
        var that = this;
        this.api.createGame(this.gameName, this.playerName).then(
            function (result) {
                that.message = `Bonjour ${playerName}, Bienvenue à ${gameName}`;
                that.displayStartGameButton = true;
                that.displayLoginPage = false;
                return result;
            },
            function (error) {
                that.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    joinGame(gameName, playerName) {
        this.gameName = gameName;
        this.playerName = playerName;
        var that = this;
        this.api.joinGame(this.gameName, this.playerName).then(
            function (result) {
                that.message = `Bonjour ${playerName}, Bienvenue à ${gameName}`;
                that.players = result;
                that.displayLoginPage = false;
            },
            function (error) {
                that.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    startGame() {
        var that = this;
        this.api.startGame(this.gameName).then(
            function (result) {
                that.displayStartGameButton = false;
                return result;
            },
            function (error) {
                that.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    selectPlayer(selectPlayer) {
        var that = this;
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
                that.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    updatePlayer(playerName, key, value) {
        var index = this.players.findIndex((element) => element.name === playerName);
        Vue.set(this.players[index], key, value);
    },
    onEnterInPhase(phase) {
        this.message = `Entrée dans la phase ${phase.phase}`;
        this.isNight = phase.isNight;
    },
    onClosePhase(phaseDone) {
        var killed = phaseDone.killed;
        var resurrected = phaseDone.resurrected;
        var winner = phaseDone.winner;

        if (killed) {
            this.updatePlayer(killed, 'state', 'dead');
            this.message = `${killed} a été tué`;
        }

        if (resurrected) {
            this.updatePlayer(resurrected, 'state', 'dead');
            this.message = `${resurrected} a été ressuscité`;
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
        this.updatePlayer(selectedPlayer.name, 'selected', selectedPlayer.selected);
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

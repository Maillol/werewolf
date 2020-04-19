<template>
  <div id="app">
    <div :class="{ alert: !isNight, 'alert--inverse': isNight }">
      {{ message }}
    </div>
    <join-or-create
      v-if="displayLoginPage"
      @create-game="createGame"
      @join-game="joinGame"
    />
    <div
      v-if="displayStartGameButton"
    >
      <button @click="startGame">
        Start
      </button>
    </div>
    <div>
      <player-board
        :players="players"
        :select-player="selectPlayer"
      />
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
        this.api.createGame(this.gameName, this.playerName).then(
            (result) => {
                this.message = this.$t('welcome', {playerName: playerName, townName: gameName});
                this.displayStartGameButton = true;
                this.displayLoginPage = false;
                return result;
            },
            (error) => {
                this.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    joinGame(gameName, playerName) {
        this.gameName = gameName;
        this.playerName = playerName;
        this.api.joinGame(this.gameName, this.playerName).then(
            (result) => {
                this.message = this.$t('welcome', {playerName: playerName, townName: gameName});
                this.players = result;
                this.displayLoginPage = false;
            },
            (error) => {
                this.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    startGame() {
        this.api.startGame(this.gameName).then(
            (result) => {
                this.displayStartGameButton = false;
                return result;
            },
            (error) => {
                this.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    selectPlayer(selectPlayer) {
        this.api.selectPlayer(this.gameName, selectPlayer, this.playerName).then(
            (result) => {
                if (result) {
                    console.log('player selected !');
                } else {
                    console.log('player not selected !');
                }
                return result;
            },
            (error) => {
                this.message = 'ERROR: ' + error.args[0];
            }
        );
    },
    updatePlayer(playerName, key, value) {
        var index = this.players.findIndex((element) => element.name === playerName);
        Vue.set(this.players[index], key, value);
    },
    onEnterInPhase(phase) {
        if (phase.phase === 'werewolf') {
            this.message = this.$t('werewolf-turn-starts');
        } else if (phase.phase === 'villager') {
            this.message = this.$t('villager-turn-starts');
        } else if (phase.phase === 'seer') {
            this.message = this.$t('seer-turn-starts');
        } else {
            this.message = 'Error unknown phase'
        }
        this.isNight = phase.isNight;
    },
    onClosePhase(phaseDone) {
        var killed = phaseDone.killed;
        var resurrected = phaseDone.resurrected;
        var winner = phaseDone.winner;

        if (killed) {
            this.updatePlayer(killed, 'state', 'dead');
            this.message = this.$t('player-was-killed', {playerName: killed});
        }

        if (resurrected) {
            this.updatePlayer(resurrected, 'state', 'dead');
            this.message = this.$t('player-was-resurrected', {playerName: resurrected});
        }

        if (winner) {
            if (winner === 'werewolf') {
                this.message = this.$t('werewolf-win');
            } else if (winner === 'villager') {
                this.message = this.$t('villager-win');
            } else {
                this.message = 'Error unknown role win'
            }
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

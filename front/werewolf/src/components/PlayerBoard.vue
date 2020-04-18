<template>
    <table class="table">
        <thead>
          <tr>
            <th scope="col">Player</th>
            <th scope="col">Role</th>
            <th scope="col"></th>
            <th scope="col"></th>
          </tr>
        </thead>
        <player-item
            v-for="player in players"
            v-bind:player="player"
            v-bind:key="player.name"
            v-on:player-clicked="selectPlayer(player.name)"
        ></player-item>
    </table>
</template>

<script>
import PlayerItem from './PlayerItem.vue'

export default {
  name: 'player-board',
  components: {
    PlayerItem
  },
  props: {
    players: Array,
    selectPlayer: Function
  }
}
</script>
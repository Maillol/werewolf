<template>
  <table class="table">
    <thead>
      <tr>
        <th scope="col">
          Player
        </th>
        <th scope="col">
          Role
        </th>
        <th scope="col">
          Alive
        </th>
        <th scope="col" />
        <th scope="col" />
      </tr>
    </thead>
    <player-item
      v-for="player in players"
      :key="player.name"
      :player="player"
      @player-clicked="selectPlayer(player.name)"
    />
  </table>
</template>

<script>
import PlayerItem from './PlayerItem.vue'

export default {
  name: 'PlayerBoard',
  components: {
    PlayerItem
  },
  props: {
    players: {
        type: Array,
        default: () => []
    },
    selectPlayer: {
        type: Function,
        default: () => (() => undefined)
    }
  }
}
</script>
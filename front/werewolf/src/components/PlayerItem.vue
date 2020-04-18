<template>
  <tr>
    <td>{{ player.name }}</td>
    <td><span v-if="player.role">{{ player.role }}</span></td>
    <td><button
        v-if="player.selectable"
        v-on:click="$emit('player-clicked')">{{ "kill" }}</button></td>
    <td>{{ player.selected }}</td>
  </tr>
</template>

<script>
export default {
  name: 'player-item',
  props: {
    player: Object
  }
}
</script>
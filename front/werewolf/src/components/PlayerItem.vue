<template>
  <li>
    <button
        v-bind:disabled="!player.selectable"
        v-on:click="$emit('player-clicked')">{{ player.name }}</button>
    <span v-if="player.role">{{ player.role }}</span>
    <span>{{ player.selected }}</span>
  </li>
</template>

<script>
export default {
  name: 'player-item',
  props: {
    player: Object
  }
}
</script>
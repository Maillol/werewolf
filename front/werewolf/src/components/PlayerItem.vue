<template>
  <tr :class="{'player-dead': player.state !== 'alive'}">
    <td>{{ player.name }}</td>
    <td><span v-if="player.role">{{ player.role }}</span></td>
    <td><span v-if="player.state">{{ player.state }}</span></td>
    <td>
      <button
        v-if="player.selectable"
        @click="$emit('player-clicked')"
      >
        {{ player.state === 'alive' ? $t('player-item.kill-button') : $t('player-item.resurrected-button') }}
      </button>
    </td>
    <td>{{ player.selected }}</td>
  </tr>
</template>

<script>
export default {
  name: 'PlayerItem',
  props: {
    player: {
        type: Object,
        required: true
    }
  }
}
</script>


<style lang="scss">
@import "../../node_modules/knacss/sass/_config/_variables.scss";

.player-dead {
    background: $color-danger;
}

</style>
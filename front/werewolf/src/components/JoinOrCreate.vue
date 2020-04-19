<template>
  <div class="center w33">
    <div>
      <label
        class="w100"
        for="playerName"
      >{{ $t('join-or-create-form.player-label') }}</label>
      <input
        id="playerName"
        v-model="playerName"
        class="w100"
      >
    </div>
    <div>
      <label
        class="w100"
        for="gameName"
      >{{ $t('join-or-create-form.game-label') }}</label>
      <input
        id="gameName"
        v-model="gameName"
        class="w100"
      >
    </div>
    <div class="txtcenter">
      <button
        class="btn--primary w100"
        @click="$emit('create-game', gameName, playerName)"
      >
        {{ $t('join-or-create-form.create-button') }}
      </button>
      <button
        class="w100"
        @click="$emit('join-game', gameName, playerName)"
      >
        {{ $t('join-or-create-form.join-button') }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JoinOrCreate',
  data: function () {
    return {
      playerName: '',
      gameName: ''
    }
  }
}
</script>
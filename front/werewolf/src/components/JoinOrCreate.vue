<template>
  <div class="center w33">
    <div>
      <label
        class="w100"
        for="playerName"
      >Player Name</label>
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
      >Game Name</label>
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
        Create
      </button>
      <button
        class="w100"
        @click="$emit('join-game', gameName, playerName)"
      >
        Join
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
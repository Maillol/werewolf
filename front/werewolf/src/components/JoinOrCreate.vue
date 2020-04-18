<template>
  <div class="center w33">
    <div>
        <label class="w100" for="playerName">Player Name</label>
        <input class="w100" id="playerName" v-model="playerName">
    </div>
    <div>
        <label class="w100" for="gameName">Game Name</label>
        <input class="w100" id="gameName" v-model="gameName">
    </div>
    <div class="txtcenter">
      <button class="btn--primary w100" v-on:click="$emit('create-game', gameName, playerName)">Create</button>
      <button class="w100" v-on:click="$emit('join-game', gameName, playerName)">Join</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'join-or-create',
  data: function () {
    return {
      playerName: '',
      gameName: ''
    }
  }
}
</script>
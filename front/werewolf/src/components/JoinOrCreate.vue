<template>
  <div>
    <div>
        <label for="playerName">Player Name</label>
        <input id="playerName" v-model="playerName">
    </div>
    <div>
        <label for="gameName">Game Name</label>
        <input id="gameName" v-model="gameName">
    </div>
    <button v-on:click="$emit('create-game', gameName, playerName)">Create</button>
    <button v-on:click="$emit('join-game', gameName, playerName)">Join</button>
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
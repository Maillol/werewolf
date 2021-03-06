import Vue from 'vue'
import App from './App.vue'
import i18n from './i18n'

Vue.config.productionTip = false


var app = new Vue({
  i18n,
  render: h => h(App)
});
app.$mount('#app')
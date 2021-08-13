import Vue from 'vue'
import App from './App.vue'

import '@/styles/global/reset.scss'
import '@/styles/global/app.scss'

Vue.config.productionTip = false
Vue.config.silent = true
new Vue({
  render: h => h(App)
}).$mount('#app')

import 'material-design-icons-iconfont/dist/material-design-icons.css'
import Vue from 'vue'
import VueResource from 'vue-resource'
import Vuetify from 'vuetify'
import App from './App'
import router from './router'
import 'vuetify/dist/vuetify.min.css'
import Vuex from 'vuex'
import  {store} from './store/store';
import vuetify from './plugins/vuetify';


Vue.use(Vuex)
Vue.use(VueResource);
Vue.http.options.root = 'http://127.0.0.1:8000';

Vue.use(Vuetify, {
  theme:{
    primary: "#FFCC80",
    secondary: "#FF9E80",
    accent: "#385f8b",
    error: "#ffa2b0",
    warning: "#ff627d",
    info: "#90CAF9",
    success: "#00E676",},
})

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
  store,
  router,
  vuetify,
  components: { App }
}).$mount('#app')


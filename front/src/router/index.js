import Vue from 'vue'
import Router from 'vue-router'



import Main from '@/components/Main'
import Results from '@/components/Results'
import ListResults from '@/components/ListResults'
import App from '@/App'

Vue.use(Router)


export default new Router({
  routes: [
    {
      path: '/',
      name: 'Main',
      component: Main
    },
    {
      path: '/result/:file',
      name: 'Results',
      component: Results
    },
    {
      path: '/results',
      name: 'ListResults',
      component: ListResults
    },
    {
      path: '/upload',
      name: 'Upload',
      component: App
    },

  ]
})

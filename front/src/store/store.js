import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export const store = new Vuex.Store({
  state: {
    uploader: null,
    analyzing_files: [{file:'some_File.exe', isAnalyzing: true}],

    malicious_threshold: 0.8,
    completed: [
      {
        time: '1 sec',
        location: 'F:/PeFiles/L.exe',
        name: 'L1.exe',
        info: "Some information",
        prediction: 0.2,
        malicious: false
      },
    ],
  },

  getters:{
    getAnalyzingFiles: state => {
      return state.analyzing_files;
    },
    getThresh(state){
      return state.malicious_threshold;
    },
    getCompleted(state){
      for(let i in state.completed){
        state.completed[i].malicious=state.completed[i].prediction > state.malicious_threshold;
      }
      return state.completed
    },
  },

  mutations:{
    addAnalyzingFile(state,{file, isAnalyzing}){
      state.analyzing_files.push({file:file, isAnalyzing:isAnalyzing});
    },
    clearAnalyzes: state =>{
      state.analyzing_files = [];
    },

    setThresh(state, thresh){
      state.malicious_threshold = thresh;
    },
    addCompleted(state, compl){
      state.completed.push({
        time: compl.time,
        location: compl.location,
        name: compl.name,
        info: compl.info,
        prediction: compl.prediction,
        malicious: true,
      },)
    },
    clearCompleted: state=>{
      state.completed = [];
    },
  }
});

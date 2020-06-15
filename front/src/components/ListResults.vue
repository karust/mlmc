<template>
  <v-container>
      <v-flex xs12 lg6 offset-lg3>
        <v-layout row wrap>

          <v-flex xs12>
            <v-text-field v-model="search"  append-icon="search" label="Search"></v-text-field>
          </v-flex>

          <v-flex xs5 offset-xs1>
            <v-switch :label="'Hide Legal'" v-model="hide_malicious" color="info"></v-switch>
          </v-flex>

          <v-flex xs5 offset-xs1>
            <v-switch :label="'Hide Malicious'" v-model="hide_legal" color="info"></v-switch>
          </v-flex>

          <v-flex xs12>
            <v-slider thumb-label :hint="'Files above '+malicious_thresh.toString()+' will be considered as malware.'"
                      :min="0.0" :max="1.0" step="0.01" v-model="malicious_thresh" label="Threshold"></v-slider>
            <br/>
          </v-flex>


          <v-flex xs6>
            <span class="body-2 warning--text" >Malwares: {{malwares}}</span>
          </v-flex>

          <v-flex xs6>
            <span class="body-2 success--text">Legitimate: {{results.length-malwares}} </span>
          </v-flex>

          <v-flex xs12>
            <v-card>
              <v-list two-line>
                <span v-show="results.length===0">No results now.</span>
                <template v-for="(item, index) in results">
                  <v-list-tile v-if="item.name.toLowerCase().includes(search.toLowerCase()) &&
                  !(!item.malicious && hide_malicious) && !(item.malicious && hide_legal)"
                               :key="item.name" :to="'/result/'+item.name" ripple>

                    <v-list-tile-content>
                      <v-list-tile-title>{{ item.name }}</v-list-tile-title>
                      <v-list-tile-sub-title class="text--primary">{{ item.location }}</v-list-tile-sub-title>
                      <v-list-tile-sub-title>Analysis time: <strong>{{ parseFloat(item.time).toFixed(3) }}</strong> seconds</v-list-tile-sub-title>
                    </v-list-tile-content>

                    <v-list-tile-action>
                      <v-list-tile-action-text><strong>{{parseFloat(item.prediction).toFixed(3)}}%</strong></v-list-tile-action-text>
                      <v-icon v-if="!item.malicious"  color="success">check_circle</v-icon>
                      <v-icon v-else color="red lighten-1">bug_report</v-icon>
                    </v-list-tile-action>

                  </v-list-tile>
                  <v-divider v-if="index + 1 < results.length" :key="index"></v-divider>
                </template>
              </v-list>
            </v-card>
          </v-flex>

        </v-layout>
      </v-flex>
  </v-container>
</template>

<script>
  import {mapGetters, mapMutations} from 'vuex'
  export default {
    props:{
      app: Object,
    },
    data(){
      return{
        search: '',
        hide_malicious: false,
        hide_legal: false,
      }
    },
    computed:{
      ...mapGetters({
        results: 'getCompleted',
      }),
      malicious_thresh: {
        get () { return this.$store.state.malicious_threshold },
        set (v) { this.$store.commit('setThresh', v) }
      },
      malwares : function(){
        let c = 0;
        for (let i in this.results){
          if(this.results[i].prediction > this.malicious_thresh) c++;
        }
        return c;
      },
    },
    methods: {
      ...mapMutations({
        addResult:'addCompleted',
        clearResults:'clearCompleted',
      }),

      completed(){
        this.resource.getCompleted({}).then(response => {
          this.clearResults();
          for(let i in response.body){
            if(response.body.hasOwnProperty(i)){
              let anl = response.body[i];
              this.addResult(anl);
            }
          }
        }, response  => {
          console.log('Server is unavailable now, please try it again later.', response);
        });
      },
      malw_count(){
        let c = 0;
        for (let i in this.results){
          if(this.results[i].prediction > this.malicious_thresh) c++;
        }
        return c;
      },
    },

    created(){
      const customActions = {
        getCompleted: {method: 'GET', url: 'completed'},
      };
      this.resource = this.$resource('', {}, customActions);
    },

    mounted(){
      this.app.title = "Analysis results";
      this.app.$refs.btnBack.style.display = '';
      this.app.$refs.btnResults.style.display = 'none';
      this.app.navbtn_to = '/';
      this.completed();
    },
    updated(){

    }
  }

</script>

<style scoped>

</style>

<template>
  <v-card>
  <v-list two-line>
    <template v-for="(item, index) in analyzing">
      <v-list-tile ripple>
        <v-list-tile-content>
          <v-list-tile-title>{{item.file}}</v-list-tile-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-progress-circular v-if="item.isAnalyzing===true" indeterminate color="secondary"></v-progress-circular>
          <v-icon v-else-if="item.isAnalyzing==='NotPE'" flat color="error" :size="35">thumb_down</v-icon>
          <v-icon v-else flat color="success" :size="35">done</v-icon>
        </v-list-tile-action>
      </v-list-tile>
      <v-divider v-if="index + 1 < analyzing.length" :key="index"></v-divider>
    </template>
  </v-list>
    </v-card>
</template>

<script>
  import {mapGetters, mapMutations} from 'vuex'
  export default {
    name: "Analyzing",
    data(){
      return{
        update: true,
      }
    },

    computed:{
      ...mapGetters({
        analyzing: 'getAnalyzingFiles',
      }),
    },

    methods:{
      ...mapMutations({
        addFiles:'addAnalyzingFile',
        clearFiles:'clearAnalyzes',
      }),
      analyzes(){
        this.resource.getAnalyzing({}).then(response => {
          this.clearFiles();
          for(let i in response.body){
            if(response.body.hasOwnProperty(i)){
              let anl = response.body[i];
              this.addFiles({file:i, isAnalyzing:anl});
            }
          }
        }, response  => {
          console.log('Server is unavailable now, please try it again later.');
        });
      },
    },

    created(){
      const customActions = {
        getAnalyzing: {method: 'GET', url: 'analyzes'},
      };
      this.resource = this.$resource('', {}, customActions);
    },

    mounted() {
      this.analyzes();
      this.upd_interval = setInterval(function () {
        if(this.update)this.analyzes();
        else clearInterval(this.upd_interval);
      }.bind(this), 1000);
    },

    beforeDestroy: function(){
      clearInterval(this.upd_interval);
    }
  }
</script>

<style scoped>
</style>

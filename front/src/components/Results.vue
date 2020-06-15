<template>
  <v-container>
    <v-flex xs12 md10 lg8 xl6 offset-md1 offset-lg2 offset-xl3>
    <div>
      <v-alert v-model="alert" :type="alert_mode" dismissible>
        {{alert_text}}
      </v-alert>
    </div>

    <br/>

    <p class="headline" slot="activator" >{{filename}}
      <v-btn flat icon color="orange darken-2" @click="getResult()">
        <v-icon>autorenew</v-icon>
      </v-btn>
    </p>

    <span v-if="certainty > 0.5" class="headline warning--text">Malware certainty: {{parseFloat(certainty).toFixed(3)}}%</span>
    <span v-else class="headline success--text">Malware certainty: {{parseFloat(certainty).toFixed(3)}}%</span>

    <br/>
      <v-container class="results">
        <v-text-field v-model="search"  append-icon="search" label="Search"></v-text-field>

        <v-data-table :headers="headers" :items="static_results" :search="search" hide-actions
                      class="elevation-1 yellow lighten-3">
          <template slot="items" slot-scope="props">
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.value }}</td>
          </template>

          <v-alert slot="no-results" :value="true" color="error" icon="warning">
            Your search for "{{ search }}" found no results.
          </v-alert>
        </v-data-table>
      </v-container>
    </v-flex>
  </v-container>
</template>

<script>
  export default {
    props:{
      app: Object,
    },
    data () {
      return {
        alert: false,
        alert_text: '',
        alert_mode: 'success',

        search: '',
        certainty: '0',
        headers: [
          {
            text: 'Feature',
            align: 'center',
            value: 'name'
          },
          { text: 'Value',
            align: 'center',
            value: 'value' },
        ],
        static_results: [
        ]
      }
    },
    methods:{
      getResult(){
        this.resource.getResults({filename:this.filename}).then(response => {
          let resp = response.body;
          this.static_results= [];
          for(let i in resp){
            let val = resp[i];
            let nam = i;
            if (nam === "signature_trusted"){
              if(val===null) val="No signature found."
            }
            else if(nam==="imports"){
              if(val!==null) val="Number of imports: " + val.length
            }
            else if(nam==="prediction"){
               this.certainty = val*100;
               continue;
            }
            let r = {name:nam, value:val};
            this.static_results.push(r);
          }

          if(response.status === 204){
            this.alert=true;
            this.alert_mode='warning';
            this.alert_text = this.filename+' file results not found';
          }
        }, response  => {
          console.log(response)
          this.alert=true;
          this.alert_mode='error';
          this.alert_text = 'Server is unavailable now, please try it again later.';
        });
      },
    },
    mounted(){
      this.app.title = "Static analyzer";
      this.app.$refs.btnBack.style.display = '';
      this.app.$refs.btnResults.style.display = 'none';
      this.app.navbtn_to = '/results'
    },
    created(){
      this.filename = this.$route.params.file;
      const customActions = {
        getResults: {method: 'GET', url: 'results'},
      };
      this.resource = this.$resource('', {}, customActions);

      this.getResult()
    },
  }
</script>

<style scoped>
.results{
}
</style>

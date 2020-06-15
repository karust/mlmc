<template>
  <v-container justify-center>
    <v-layout wrap>
      <v-flex xs12 lg8 offset-lg2>
      <!--uploader-drop class="dropzone">
        <uploader-btn :attrs="attrs">Select file</uploader-btn>
        <uploader-btn :directory="true">Select folder</uploader-btn>
      </uploader-drop-->
      <v-file-input v-model="files" color="deep-purple accent-4" counter label="File input" multiple
        placeholder="Select your files" prepend-icon="mdi-paperclip" outlined :show-size="1000">
        <template v-slot:selection="{ index, text }">
          <v-chip v-if="index < 2" color="deep-purple accent-4" dark label small>
            {{ text }}
          </v-chip>

          <span v-else-if="index === 2" class="overline grey--text text--darken-3 mx-2">
            +{{ files.length - 2 }} File(s)
          </span>
        </template>
      </v-file-input>
      <br/>

      <v-tabs slot="extension" v-model="tabs" fixed-tabs  color="transparent">
        <v-tabs-slider></v-tabs-slider>
        <v-tab href="#uploads" class="primary--text">
          <v-icon large color="primary">cloud_upload</v-icon>
        </v-tab>
        <v-tab href="#processing" class="primary--text">
          <v-icon large color="primary">schedule</v-icon>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tabs" class="white elevation-1">
        <br/>
        <v-tab-item :value="'uploads'">
          <p class="title">Uploading files.</p>
          <!--uploader-list :file-list="fileList" class="uploader"></uploader-list-->
        </v-tab-item>
        <v-tab-item :value="'processing'">
          <p class="title">Analyzing files.</p>
          <analyzing></analyzing>
        </v-tab-item>
      </v-tabs-items>
  </v-flex>
</v-layout>

  </v-container>
</template>

<script>
  //import { kebabCase } from '../common/utils'
  import Analyzing from "./Analyzing";
  const FILE_ADDED_EVENT = 'fileAdded'
  const FILES_ADDED_EVENT = 'filesAdded'

  export default {
    components: {Analyzing},
    props: {
      app: Object,
      autoStart: {
        type: Boolean,
        default: true
      },
      fileStatusText: {
        type: Object,
        default () {
          return {
            success: 'success',
            error: 'error',
            uploading: 'uploading',
            paused: 'paused',
            waiting: 'waiting'
          }
        }
      }
    },

    data () {
      return {
        started: false,
        files: [],
        fileList: [],

        uploaderInstance: null,

        attrs: {
          accept: '.exe, .dll, .sys'
        },
        tabs: null,
      }
    },

    methods: {
      /* eslint-disable no-unused-vars */

      uploadStart () {
        this.started = true
      },

      fileAdded (file) {
        // this.$emit(kebabCase(FILE_ADDED_EVENT), file)
        // if (file.ignored) {
        //   // is ignored, filter it
        //   return false
        // }
      },

      filesAdded (files, fileList) {
        // this.$emit(kebabCase(FILES_ADDED_EVENT), files, fileList)
        // if (files.ignored || fileList.ignored) {
        //   // is ignored, filter it
        //   return false
        // }
      },

      fileRemoved () {
        this.files = this.$store.state.uploader.files
        this.fileList = this.$store.state.uploader.fileList
      },

      filesSubmitted () {
        this.files = this.$store.state.uploader.files
        this.fileList = this.$store.state.uploader.fileList
        if (this.autoStart) {
          this.$store.state.uploader.upload()
        }
      },

      allEvent (...args) {
        // const name = args[0]
        // if (name === FILE_ADDED_EVENT || name === FILES_ADDED_EVENT) {
        //   return
        // }
        // args[0] = kebabCase(name)
        // this.$emit.apply(this, args)
      },
    },
    
    created () {
      this.$store.state.uploader.fileStatusText = this.fileStatusText
      this.$store.state.uploader.on('catchAll', this.allEvent)
      this.$store.state.uploader.on('uploadStart', this.uploadStart)
      this.$store.state.uploader.on(FILE_ADDED_EVENT, this.fileAdded)
      this.$store.state.uploader.on(FILES_ADDED_EVENT, this.filesAdded)
      this.$store.state.uploader.on('fileRemoved', this.fileRemoved)
      this.$store.state.uploader.on('filesSubmitted', this.filesSubmitted)
      //this.files = this.$store.state.uploader.files;
      //this.fileList = this.$store.state.uploader.fileList;
    },

    mounted(){
      this.app.title = "Drop a file in the field below";
      //this.app.$refs.btnBack.style.display = 'none';
      //this.app.$refs.btnResults.style.display = '';
      this.app.navbtn_to = '/results';
    }
  }
</script>

<style scoped>
  .main{
    position: absolute;
    min-width: 100%;
    min-height: 100%;
    top: 0;
    left: 0;
    background-color: #f0f0f0;
  }
  .dropzone{
    position: relative;
    background-image: url("../assets/extensions1.png");
    background-position: 50%, 50%;
    background-repeat: no-repeat;
    background-size: 200px 75px;
    height: 300px;
    border: 2px solid rgba(0, 0, 0, 0.45);
    width: 100%;
    cursor: pointer;
    background-color: #FFCC80;
    opacity: 1;
  }
  .dropzone:hover{
    position: relative;


    background-color: #FFFDE7;
    transition: background-color 0.2s ease-in-out;
  }
  .load-button{
    color: #363636;
    height: 40px;
    width: 100px;
    margin-right: 5%;
  }
  .load-button:hover{
    background-color: #FFCC80;
  }
  .results{
    position: relative;
  }
</style>

<script lang="ts">

import Example from './components/Example.vue'
<<<<<<< HEAD
import Contours from './components/Contours.vue'
=======
import Auxiliary from './components/Auxiliary.vue'
>>>>>>> 62cbfbfc1974011e9d855b730d9a5586c65ed74e
/*
import ExampleWithLegend from './components/ExampleWithLegend.vue';
import ExampleWithInteractions from './components/ExampleWithInteractions.vue';*/

export default {
  components: {
    Example,
    Contours,
    Auxiliary,
    /*
    ExampleWithLegend,
    ExampleWithInteractions*/
  }
}
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
    <v-row no-gutters>
      <v-col cols="7">
        <Contours />
      </v-col>
      <v-col>
        <Auxiliary />
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
#main-container{
  height: 100%;
}
</style>

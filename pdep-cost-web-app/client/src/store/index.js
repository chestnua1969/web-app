import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
// import {csvParse} from 'd3-dsv';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    baseData: null,
    optimizationParameters: null
  },
  mutations: {},
  actions: {
    parseData({ state }) {
      axios
        .get("base-data.json", {
          baseURL: window.location.href.split("/index")[0]
        })
        .then(res => {
          state.baseData = res.data;
        })
        .catch(err => {
          console.log(`Error parsing data: ${err}`);
        });

      axios
        .get("optimization-parameters.json", {
          baseURL: window.location.href.split("/index")[0]
        })
        .then(res => {
          state.optimizationParameters = res.data;
        })
        .catch(err => {
          console.log(`Error parsing data: ${err}`);
        });
    }
  }
});

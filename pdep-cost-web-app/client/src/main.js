import "bulma/css/bulma.min.css";
import Vue from "vue";
import App from "./App.vue";
import store from "@/store/index";

import { library } from "@fortawesome/fontawesome-svg-core";
import {
  faHome,
  faChartBar,
  faSlidersH,
  faServer
} from "@fortawesome/free-solid-svg-icons";
import {
  FontAwesomeIcon,
  FontAwesomeLayers
} from "@fortawesome/vue-fontawesome";

library.add(faHome, faChartBar, faSlidersH, faServer);

Vue.component("font-awesome-icon", FontAwesomeIcon);
Vue.component("font-awesome-layers", FontAwesomeLayers);

import LoaderSpinning from "vuesalize";
import 'vuesalize/dist/vuesalize.css'

Vue.use(LoaderSpinning);

Vue.config.productionTip = false;

new Vue({
  render: h => h(App),
  store
}).$mount("#app");

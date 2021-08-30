<template>
  <div id="app" ref="appContainer">
    <header>
      <nav aria-label="Views menu">
        <ul>
          <li>
            <img
              :src="publicPath + '/AFGSClogo.png'"
              width="40"
              style="margin-right: 10px;"
            />
            <h1 class="title is-3">
              Portfolio Level Digital Engineering Platform
            </h1>
          </li>
          <li
            v-for="(tab, index) in activeTab"
            :key="index"
            class="tab"
            :class="{ active: tab.active }"
            @click="tabSelected = tab"
          >
            <font-awesome-icon
              :icon="tab.icon"
              style="margin-right: 7px;"
            ></font-awesome-icon>
            {{ tab.name }}
          </li>
        </ul>
      </nav>
    </header>

    <overview v-show="tabSelected.name === 'Overview'"></overview>
    <setup v-show="tabSelected.name === 'Setup'"></setup>
    <optimization-results
      v-show="tabSelected.name === 'Optimization Results'"
    ></optimization-results>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import Overview from "./components/Overview";
import Setup from './components/Setup';
import OptimizationResults from "./components/OptimizationResults";

export default {
  name: "App",
  components: {
    Overview,
    Setup,
    OptimizationResults
  },
  data() {
    return {
      tabs: [
        // {
        //   name: "Overview",
        //   component: "Overview",
        //   icon: ["fas", "home"]
        // },
        {
          name: "Setup",
          component: "Setup",
          icon: ["fas", "sliders-h"]
        },
        {
          name: "Optimization Results",
          component: "OptimizationResults",
          icon: ["fas", "chart-bar"]
        }
      ],
      tabSelected: null
    };
  },
  computed: {
    activeTab() {
      if (this.tabSelected) {
        return this.tabs
          .map(item =>
            item.name === this.tabSelected.name
              ? { ...item, active: true }
              : { ...item, active: false }
          )
          .reverse();
      } else {
        return this.tabs.slice().reverse();
      }
    },
    publicPath() {
      return window.location.href.split("/index")[0] + "/";
    }
  },
  methods: {
    ...mapActions(["parseData"])
  },
  created() {
    this.parseData();
    this.tabSelected = this.tabs[0];
    document.title = "Portfolio Level Digital Engineering Platform";
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  min-height: 100vh;
}

header {
  height: 55px;
}

/* Navbar styles */
nav {
  align-items: center;
  width: 100%;
  height: 100%;
  color: white;
  font-size: 1rem;
  overflow-x: hidden;
  background-color: #005b94;
}

nav ul {
  list-style: none;
  height: 100%;
  padding-left: 1%;
  width: 100%;
}

nav li {
  float: left;
  margin-right: 20px;
  cursor: pointer;
  height: 100%;
  display: flex;
  align-items: center;
  border-bottom: 3px solid #005b94;
}

nav li .title {
  margin-right: 30px;
  color: white;
  font-size: 24px;
}

nav li:hover {
  opacity: 0.75;
}

nav li h1 {
  color: white;
}

.active {
  border-bottom: solid 3px white;
}

.tab {
  float: right;
}
</style>

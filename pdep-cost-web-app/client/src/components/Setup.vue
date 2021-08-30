<template>
  <main v-if="optimizationParameters">
    <div class="columns">
      <div class="column is-6 section right-border">
        <div class="title">Portfolio Overview</div>

        <div class="box" style="width: 250px;">
          <div class="metric-header">Baseline Budget</div>
          <div class="subtitle">
            {{ dollarFormat(optimizationParameters.budget) }}
          </div>
        </div>

        <div class="box">
          <div class="metric-header">Aircraft</div>
          <div
            v-for="aircraft in optimizationParameters.aircraft"
            :key="aircraft.name"
          >
            <div class="subheader">{{ aircraft.name }}</div>

            <div class="columns">
              <div class="column is-4">
                <div class="table-title">Current Metrics</div>
                <table class="table is-striped">
                  <tbody>
                    <tr v-for="entry in aircraft.metrics" :key="entry.key">
                      <td>{{ entry.description }}</td>
                      <td>{{ entry.value }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="column is-4">
                <div class="table-title">Costs</div>
                <table class="table is-striped">
                  <tbody>
                    <tr v-for="entry in aircraft.costs" :key="entry.key">
                      <td>{{ entry.description }}</td>
                      <td>{{ dollarFormat(entry.cost) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="column is-4">
                <div class="table-title">Modernization Options</div>
                <table class="table is-striped">
                  <tbody>
                    <tr
                      v-for="entry in aircraft.modernizationOptions"
                      :key="entry.key"
                    >
                      <td>{{ entry.description }}</td>
                      <td>{{ dollarFormat(entry.cost) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="column is-6 section">
        <div class="title" style="display: inline-block">COA Definition</div>
        <button
          class="button is-dark"
          @click="runOptimization"
          v-if="!optimizationRunning"
          style="float: right"
        >
          <font-awesome-icon
            :icon="['fas', 'server']"
            style="margin-right: 7px;"
          ></font-awesome-icon>
          Run Optimization
        </button>
        <loader-spinning
          v-if="optimizationRunning"
          style="float: right; margin: -15px 15px"
        ></loader-spinning>

        <div class="box">
          This is where users will define the scenarios they want to analyze.
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { mapState } from "vuex";
import axios from "axios";
import { format } from "d3-format";

export default {
  name: "Setup",

  computed: {
    ...mapState(["optimizationParameters"]),
    rootUrl() {
      return `http://${window.location.hostname}:8082`;
    }
  },

  data() {
    return {
      dollarFormat: format("$,"),
      optimizationRunning: false
    };
  },

  methods: {
    runOptimization() {
      this.optimizationRunning = true;
      axios
        .post(`${this.rootUrl}/run-optimization`, this.optimizationParameters)
        .then(res => {
          alert(res.data.message);
          this.optimizationRunning = false;
        });
    }
  }
};
</script>

<style scoped>
.section {
  padding: 30px;
}

.metric-header {
  font-size: 1.75rem;
  font-weight: normal;
}

.subheader {
  font-size: 1.5rem;
  margin: 10px 0;
}

.table-title {
  font-weight: bold;
  text-align: center;
}

.table {
  width: 100%;
  margin-bottom: 10px;
}
</style>

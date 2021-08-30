<template>
  <main v-if="baseData">
    <div class="columns">
      <div class="column is-2">
        <div class="box">
          <h3 class="metric-header">Base</h3>
          <div class="select">
            <select v-model="selectedBase">
              <option
                v-for="(base, index) in baseData"
                :value="base"
                :key="index"
              >
                {{ base.name }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <div class="column is-2">
        <div class="box">
          <h3 class="metric-header">Budget</h3>
          <h4 class="subtitle">{{ dollarFormat(selectedBase.budget) }}</h4>
        </div>
      </div>
      <div class="column is-2">
        <div class="box">
          <h3 class="metric-header">Aircraft Availability</h3>
          <h4 class="subtitle">
            {{ selectedBase.aircraftAvailability * 100 + "%" }}
          </h4>
        </div>
      </div>
    </div>

    <div class="columns">
      <div class="column is-2">
        <div class="box">
          <h3 class="metric-header">Aircraft Health</h3>
          <table class="table is-striped">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(entry, index) in selectedBase.aircraftHealth"
                :key="index"
              >
                <td>{{ entry.metric }}</td>
                <td>{{ entry.value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="column is-2">
        <div class="box">
          <h3 class="metric-header">Crew Health</h3>
          <table class="table is-striped">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(entry, index) in selectedBase.crewHealth"
                :key="index"
              >
                <td>{{ entry.metric }}</td>
                <td>{{ entry.value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="column is-2">
        <div class="box">
          <h3 class="metric-header">Missile Health</h3>
          <table class="table is-striped">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(entry, index) in selectedBase.missileHealth"
                :key="index"
              >
                <td>{{ entry.metric }}</td>
                <td>{{ entry.value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { mapState } from "vuex";
import { format } from "d3-format";

export default {
  name: "Overview",
  computed: {
    ...mapState(["baseData"])
  },
  data() {
    return {
      dollarFormat: format("$,"),
      selectedBase: null
    };
  },
  watch: {
    baseData: {
      handler() {
        if (!this.selectedBase && this.baseData.length)
          this.selectedBase = this.baseData[0];
      }
    }
  }
};
</script>

<style scoped>
main {
  padding: 20px;
}

.metric-header {
  font-size: 1.75rem;
  font-weight: normal;
}

.box {
  height: 100%;
}

.table {
  width: 100%;
}
</style>

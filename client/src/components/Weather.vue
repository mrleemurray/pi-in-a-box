<template>
  <div v-text="weather.metric.weather[0].description"></div>
</template>

<script>
var weather = require('openweather-apis')

export default {
  name: 'Weather',

  components: {},
  props: {},
  data() {
    return {
      pollWeather: null,
      weather: {
          metric: {},
          imperial: {}
      }
    }
  },

  computed: {},

  created() {},

  mounted() {
    this.configureWeather('metric')
    this.getLatestWeather()
    this.setDataInterval()
  },

  beforeDestroy() {
    clearInterval(this.pollWeather)
  },

  methods: {
    /**
     * Poll OpenWeather for data.
     */
    setDataInterval() {
      clearInterval(this.pollWeather)
      this.pollWeather = setInterval(() => {
        this.getLatestWeather()
      }, 60 * 15 * 1000)
    },

    configureWeather(units) {
      weather.setLang('en')
      weather.setCity('Walthamstow')
      weather.setUnits(units)
      weather.setAPPID(process.env.VUE_APP_OPENWEATHER_APP_ID)
    },
    getLatestWeather() {
      var self = this;
      weather.setUnits('metric')
      weather.getAllWeather((err, JSONObj) => {
        self.weather.metric = JSONObj
      })
      weather.setUnits('imperial')
      weather.getAllWeather((err, JSONObj) => {
        self.weather.imperial = JSONObj
      })
      console.info(this.weather)
    }
  },

  watch: {}
}
</script>

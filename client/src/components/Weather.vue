<template>
  <div></div>
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
      weather: null
    }
  },

  computed: {},

  created() {},

  mounted() {
    this.configureWeather('metric')
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
        this.getNowPlaying()
      }, 60 * 15 * 1000)
    },

    configureWeather(units) {
      weather.setLang('en')
      weather.setCity('Walthamstow')
      weather.setUnits(units)
      weather.setAPPID(process.env.VUE_APP_OPENWEATHER_APP_ID)
    },
    getLatestWeather() {
      weather.getTemperature(function(err, temp) {
        console.log(temp)
      })
      weather.getSmartJSON(function(err, desc) {
        console.log(desc)
      })
      weather.getAllWeather(function(err, JSONObj) {
        console.log(JSONObj)
        this.weather = JSONObj
      })
    }
  },

  watch: {}
}
</script>

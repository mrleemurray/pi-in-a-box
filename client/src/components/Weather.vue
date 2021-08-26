<template>
  <div v-if="(weather.metric !== null) && (weather.imperial !== null)" class="weather">
      <div class="weather__cover">
            <transition name="fade">
                <img
                :src="weather.image"
                :alt="weather.metric.weather[0].description"
                :key="weather.dt"
                class="weather__image"
                />
                
            </transition>
        </div>
        <div class="weather__details">
            <h1
                class="weather__temperature"
                v-text="temperature()"
            />
            <h2
                class="weather__humidity"
                v-text="weather.metric.main.humidity"
            />
        </div>
  </div>
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
          metric: null,
          imperial: null,
          image: null
      }
    }
  },

  computed: {
      
  },

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
        self.weather.image = `https://source.unsplash.com/720x720/?${self.weather.metric.weather[0].description.replace(/ /g, ",")}`
      })
      weather.setUnits('imperial')
      weather.getAllWeather((err, JSONObj) => {
        self.weather.imperial = JSONObj
      })
      console.info(this.weather)
    },
    temperature(){
        return `${Math.round(this.weather.metric.main.temp)}°C / ${Math.round(this.weather.imperial.main.temp)}°F`
      }
  },

  watch: {}
}
</script>

<style src="@/styles/components/weather.scss" lang="scss" scoped></style>

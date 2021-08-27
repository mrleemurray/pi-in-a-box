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
            <p
                class="weather__temperature"
            >
                <span v-text="formatTemperature(weather.imperial.main.temp, 'imperial')"/>
                <span class="weather__divider">/</span>
                <span v-text="formatTemperature(weather.metric.main.temp, 'metric')"/>
            </p>
            <div :class="isTempFeelDifferent(weather.imperial.main)">
            <p class="weather__description">Feels like</p>
            <p
                class="weather__temperature weather__feel"
            >
                <span v-text="formatTemperature(weather.imperial.main.feels_like, 'imperial')"/>
                <span class="weather__divider">/</span>
                <span v-text="formatTemperature(weather.metric.main.feels_like, 'metric')"/>
            </p>
            </div>
            <div class="weather__extra">
                <div class="weather__section">
                <p class="weather__description weather__smaller">Humidity</p>
                <p
                    class="weather__humidity"
                    v-text="formatHumidity(weather.metric.main.humidity)"
                />
                </div>
                <div class="weather__section">
                <p class="weather__description weather__smaller">Wind</p>
                <p
                    class="weather__humidity"
                    v-text="formatWind(weather.imperial.wind.speed)"
                />
                </div>
                <div class="weather__section">
                <p class="weather__description weather__smaller">Gusts</p>
                <p
                    class="weather__humidity"
                    v-text="formatWind(weather.imperial.wind.gust)"
                />
                </div>
            </div>
        </div>
  </div>
</template>

<script>
var weather = require('openweather-apis')

const METRIC = 'metric'
const IMPERIAL = 'imperial'

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
      weather.setUnits(METRIC)
      weather.getAllWeather((err, JSONObj) => {
        self.weather.metric = JSONObj
        self.weather.image = `https://source.unsplash.com/720x720/?${self.weather.metric.weather[0].description.replace(/ /g, ",")}`
      })
      weather.setUnits(IMPERIAL)
      weather.getAllWeather((err, JSONObj) => {
        self.weather.imperial = JSONObj
      })
      console.info(this.weather)
    },
    temperature(){
        return `${Math.round(this.weather.metric.main.temp)}°C / ${Math.round(this.weather.imperial.main.temp)}°F`
    },
    formatTemperature(temp, unit) {
        console.info(unit)
        if (unit === 'metric'){
            return `${Math.round(temp)}°C`
        } else {
            return `${Math.round(temp)}°F`
        }
    },
    formatHumidity(humidity) {
        return `${humidity}%`
    },
    formatWind(speed) {
        return `${Math.round(speed)}mph`
    },
    isTempFeelDifferent(temperature){
        if (Math.round(temperature.temp) == Math.round(temperature.feels_like)){
            return 'weather--opacity-0'
        }
        return ''
    }
  },

  watch: {}
}
</script>

<style src="@/styles/components/weather.scss" lang="scss" scoped></style>

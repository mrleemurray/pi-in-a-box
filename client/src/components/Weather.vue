<template>
  <div v-if="(weather.metric !== null) && (weather.imperial !== null)" class="weather">
      <div class="weather__cover">
            <transition name="fade">
                <img
                :src="weather.image"
                :alt="weather.metric.weather[0].description"
                :key="weather.dt"
                class="weather__image"
                :class="imageOpacity(size)"
                />
            </transition>
        </div>
        <div class="weather__details" :class="detailOpacity(size, 'large')">
            <p
                class="weather__overview"
            >
                <span v-text="formatOverview(weather)"/>
            </p>
            <p
                class="weather__temperature"
            >
                <span v-text="formatTemperature(weather.imperial.main.temp, 'imperial')"/>
                <span class="weather__divider">/</span>
                <span v-text="formatTemperature(weather.metric.main.temp, 'metric')"/>
            </p>
        </div>
        <div class="weather__details--medium" :class="detailOpacity(size, 'medium')">
            <div class="weather__icons--medium">
            <i class="wi weather__icon--medium"
                :class="formatWeatherIcon(weather.metric.weather[0].id)"></i>
                <i class="wi wi-wind weather__icon--medium weather__icon-wind"
                :class="formatWindIcon(weather.metric.wind.deg)"
                ></i>
            </div>
                <p
                class="weather__temperature weather__temperature--medium"
            >
                <span v-text="formatTemperature(weather.imperial.main.temp, 'imperial')"/>
                <span class="weather__divider">/</span>
                <span v-text="formatTemperature(weather.metric.main.temp, 'metric')"/>
            </p>
        </div>
        <div class="weather__details--medium" :class="detailOpacity(size, 'small')">
            <div class="weather__icons--medium">
            <i class="wi weather__icon--medium"
                :class="formatWeatherIcon(weather.metric.weather[0].id)"></i>
                <i class="wi wi-wind weather__icon--medium weather__icon-wind"
                :class="formatWindIcon(weather.metric.wind.deg)"
                ></i>
            </div>
                <p
                class="weather__temperature weather__temperature--medium"
            >
                <span v-text="formatTemperature(weather.imperial.main.temp, 'imperial')"/>
                <span class="weather__divider">/</span>
                <span v-text="formatTemperature(weather.metric.main.temp, 'metric')"/>
            </p>
        </div>
  </div>
</template>

<script>
var weather = require('openweather-apis')
var colorScale = require('color-scales')

const METRIC = 'metric'
const IMPERIAL = 'imperial'

const LARGE = 'large'
const MEDIUM = 'medium'
const SMALL = 'small'
// const XSMALL = 'xsmall'

export default {
  name: 'Weather',

  components: {},
  props: {
      size: {
          type: String,
          default: MEDIUM
      }
  },
  data() {
    return {
      pollWeather: null,
      weather: {
          metric: null,
          imperial: null,
          image: null
      },
      colorScaleLight: null,
      colorScaleDark: null
    }
  },

  computed: {
  },

  created() {},

  mounted() {
    this.configureWeather('metric')
    this.colorScaleLight = new colorScale(-5, 35, ["#D01B1B", "#ffffff", "#47abd8"])
    this.colorScaleDark = new colorScale(-5, 35, ["#D01B1B", "#000000", "#47abd8"])
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
        self.updateTemperatureColor(self.weather.metric.main.temp)
      })
    //   weather.getWeatherOneCall((err, data) => {
    //         console.info('?')
    //         console.info(data)
    //     });
      console.info(this.weather)
    },
    temperature(){
        return `${Math.round(this.weather.metric.main.temp)}°C / ${Math.round(this.weather.imperial.main.temp)}°F`
    },
    formatTemperature(temp, unit) {
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
    formatWindIcon(deg) {
        return `towards-${deg}-deg`
    },
    windDescription(speed) {
        // https://www.rmets.org/resource/beaufort-scale
        if (speed < 1) {
            return 'calm'
        }
        if (speed >= 1 && speed < 4) {
            return 'light air'
        }
        if (speed >= 4 && speed < 8) {
            return 'a light breeze'
        }
        if (speed >= 8 && speed < 13) {
            return 'a gentle breeze'
        }
        if (speed >= 13 && speed < 19) {
            return 'a moderate breeze'
        }
        if (speed >= 19 && speed < 25) {
            return 'a fresh breeze'
        }
        if (speed >= 25 && speed < 32) {
            return 'a strong breeze'
        }
        if (speed >= 32 && speed < 39) {
            return 'a near gale'
        }
        if (speed >= 39 && speed < 47) {
            return 'a gale'
        }
        if (speed >= 47 && speed < 55) {
            return 'a strong gale'
        }
        if (speed >= 55 && speed < 64) {
            return 'stormy'
        }
        if (speed >= 64 && speed < 73) {
            return 'violently stormy'
        }
        if (speed >= 74) {
            return 'hurricane conditions'
        }
        return ``
    },
    humidityDescription(humidity) {
        if (humidity >= 0 && humidity < 25) {
            return 'very dry'
        }
        if (humidity >= 25 && humidity < 30) {
            return 'slightly dry'
        }
        if (humidity >= 30 && humidity < 60) {
            return 'dry'
        }
        if (humidity >= 60 && humidity < 70) {
            return 'slightly humid'
        }
        if (humidity >= 70 && humidity < 80) {
            return 'humid'
        }
        if (humidity >= 80) {
            return 'very humid'
        }
        return ``
    },
    formatOverview(weather) {
        var windDescription = this.windDescription(weather.imperial.wind.speed)
        var humidityDescription = this.humidityDescription(weather.metric.main.humidity)
        if (weather.imperial.wind.speed)
        return `${weather.imperial.weather[0].description}, ${humidityDescription} and ${windDescription}`
    },
    formatWeatherIcon(id) {
        return `wi-owm-${id}`
    },
    isTempFeelDifferent(temperature){
        if (Math.round(temperature.temp) == Math.round(temperature.feels_like)){
            return 'weather--opacity-0'
        }
        return ''
    },
    imageOpacity(size) {
        if (size == LARGE) {
            return 'weather--opacity-50'
        }
        if (size == MEDIUM) {
            return 'weather--opacity-20'
        }
        if (size == SMALL) {
            return 'weather--opacity-10'
        }
        return 'weather--opacity-0'
    },
    detailOpacity(size, validSize) {
        if (size != validSize) {
            return 'weather--opacity-0'
        }
        return ''
    },
    updateTemperatureColor(temperature) {
        let hexStrLight = this.colorScaleLight.getColor(temperature).toHexString()
        let hexStrDark = this.colorScaleDark.getColor(temperature).toHexString()
        document.documentElement.style.setProperty(
            '--color-temperature',
            hexStrLight
        )
        document.documentElement.style.setProperty(
            '--color-temperature-dark',
            `${hexStrDark}77`
        )
        document.documentElement.style.setProperty(
            '--color-temperature-dark-solid',
            hexStrDark
        )
    }
  },

  watch: {}
}
</script>

<style src="@/styles/components/weather.scss" lang="scss" scoped></style>

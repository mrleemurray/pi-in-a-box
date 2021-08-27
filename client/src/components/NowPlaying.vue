<template>
  <div id="app">
    <div
      v-if="player.playing"
      class="now-playing"
      :class="getNowPlayingClass()"
    >
      <transition name="fade">
        <div class="now-playing__cover" :class="getArtworkOpacity()">
          <transition name="fade">
            <img
              :src="player.trackAlbum.image"
              :alt="player.trackTitle"
              :key="player.trackTitle"
              class="now-playing__image"
            />
          </transition>
        </div>
      </transition>
      <div class="now-playing__details">
        <h1
          class="now-playing__track"
          :class="getDetailOpacity()"
          v-text="player.trackTitle"
        />
        <h2
          class="now-playing__artists"
          :class="getDetailOpacity()"
          v-text="getTrackArtists"
        />
        <!-- <div class="controls">
          <button @click="managePlayback('prev')">Prev</button>
          <button @click="managePlayback('shuffle')">Shuffle</button>
          <button @click="managePlayback('next')">Next</button>
        </div> -->
      </div>
      <div class="now-playing__summary">
        <div class="scroll-left" :class="getScrollTextOpacity()">
          <p v-text="player.trackTitle + ' - ' + getTrackArtists" />
        </div>
      </div>
    </div>
    <div v-else class="now-playing" :class="getNowPlayingClass()">
      <transition name="fade">
        <weather></weather>
      </transition>
    </div>
  </div>
</template>

<script>
var mqtt = require('mqtt')
var client = mqtt.connect(
  `mqtt://${process.env.VUE_APP_MQTT_BROKER_HOST_ADDRESS}`
)

import props from '@/utils/props.js'
import Weather from './Weather.vue'

const OPEN_100_PERCENT = 1.0
// const OPEN_66_PERCENT = 0.66
const OPEN_50_PERCENT = 0.5
// const OPEN_33_PERCENT = 0.33
const OPEN_25_PERCENT = 0.2
// const OPEN_1_PERCENT = 0.01
const OPEN_0_PERCENT = 0

// const FAST_SPEED = 0.05;
const MEDIUM_SPEED = 0.03;
const SLOW_SPEED = 0.02;

const SCHEDULE = 'SCHEDULE'
const TAP = 'TAP'
const LONG_PRESS = 'LONG_PRESS'

const LID_POSITION_CHANNEL = 'hardware/output/lid/position'
const TOUCH_INPUT_CHANNEL = 'hardware/input/touch'
const SCHEDULE_INPUT_CHANNEL = 'schedule/lid/position'

export default {
  name: 'NowPlaying',
  components: {
    Weather
  },
  props: {
    auth: props.auth,
    endpoints: props.endpoints,
    player: props.player
  },

  data() {
    return {
      pollPlaying: '',
      playerResponse: {},
      playerData: this.getEmptyPlayer(),
      colourPalette: '',
      swatches: [],
      previousPlayState: null,
      currentLidPosition: OPEN_0_PERCENT,
      previousLidPosition: OPEN_0_PERCENT,
      lastInputType: SCHEDULE
    }
  },

  computed: {
    /**
     * Return a comma-separated list of track artists.
     * @return {String}
     */
    getTrackArtists() {
      return this.player.trackArtists.join(', ')
    }
  },

  mounted() {
    this.setDataInterval()
    this.configureMQTT()
  },

  beforeDestroy() {
    clearInterval(this.pollPlaying)
  },

  methods: {
    async managePlayback(command) {
      var cmd = 'next'
      var method = 'POST'
      if (command === 'next') {
        cmd = this.endpoints.nextTrack
      }
      if (command === 'prev') {
        cmd = this.endpoints.prevTrack
      }
      if (command === 'shuffle') {
        cmd = `${this.endpoints.shuffle}?state=true`
        method = 'PUT'
      }
      try {
        const response = await fetch(`${this.endpoints.base}/${cmd}`, {
          method: method,
          headers: {
            Authorization: `Bearer ${this.auth.accessToken}`
          }
        })
        /**
         * Fetch error.
         */
        if (!response.ok) {
          throw new Error(`An error has occured: ${response.status}`)
        }
        /**
         * Spotify returns a 204 when no current device session is found.
         * The connection was successful but there's no content to return.
         */
        if (response.status === 204) {
          if (command === 'shuffle') {
            this.managePlayback('next')
          }
          return
        }
      } catch (error) {
        console.error(error)
      }
    },
    getArtworkOpacity() {
      if (this.displayState === OPEN_50_PERCENT) {
        return 'now-playing--opacity-20'
      }
      if (
        this.displayState === OPEN_25_PERCENT ||
        this.displayState === OPEN_0_PERCENT
      ) {
        return 'now-playing--opacity-0'
      }
      return ''
    },
    getDetailOpacity() {
      if (this.displayState !== OPEN_50_PERCENT) {
        return 'now-playing--opacity-0'
      }
      return ''
    },
    getScrollTextOpacity() {
      if (this.displayState !== OPEN_25_PERCENT) {
        return 'now-playing--opacity-0'
      }
      return ''
    },
    updateHardwareState(playState) {
      if (playState !== this.previousPlayState) {
        var newLidPosition = playState ? '1.0,0.02' : '0.0,0.02'
        client.publish(LID_POSITION_CHANNEL, newLidPosition)
      }
      this.previousPlayState = playState
    },
    /**
     * Make the network request to Spotify to
     * get the current played track.
     */
    async getNowPlaying() {
      let data = {}
      try {
        const response = await fetch(
          `${this.endpoints.base}/${this.endpoints.nowPlaying}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth.accessToken}`
            }
          }
        )

        /**
         * Fetch error.
         */
        if (!response.ok) {
          throw new Error(`An error has occured: ${response.status}`)
        }

        /**
         * Spotify returns a 204 when no current device session is found.
         * The connection was successful but there's no content to return.
         */
        if (response.status === 204) {
          data = this.getEmptyPlayer()
          this.playerData = data
          // this.updateHardwareState(this.playerData.playing)

          this.$nextTick(() => {
            this.$emit('spotifyTrackUpdated', data)
          })
          return
        }

        data = await response.json()
        this.playerResponse = data
        // this.updateHardwareState(this.playerData.playing)
      } catch (error) {
        this.handleExpiredToken()
        data = this.getEmptyPlayer()
        this.playerData = data

        this.$nextTick(() => {
          this.$emit('spotifyTrackUpdated', data)
        })
      }
    },

    /**
     * Get the Now Playing element class.
     * @return {String}
     */
    getNowPlayingClass() {
      const playerClass = this.player.playing ? 'active' : 'idle'
      return `now-playing--${playerClass}`
    },

    /**
     * Return a formatted empty object for an idle player.
     * @return {Object}
     */
    getEmptyPlayer() {
      return {
        playing: false,
        trackAlbum: {},
        trackArtists: [],
        trackId: '',
        trackTitle: ''
      }
    },

    /**
     * Poll Spotify for data.
     */
    setDataInterval() {
      clearInterval(this.pollPlaying)
      this.pollPlaying = setInterval(() => {
        this.getNowPlaying()
      }, 5000)
    },

    /**
     * Handle newly updated Spotify Tracks.
     */
    handleNowPlaying() {
      if (
        this.playerResponse.error?.status === 401 ||
        this.playerResponse.error?.status === 400
      ) {
        window.console.log('throw error')
        this.handleExpiredToken()
        return
      }

      /**
       * Player is active, but is paused.
       */
      if (this.playerResponse.is_playing === false) {
        this.playerData = this.getEmptyPlayer()
        return
      }

      /**
       * The newly fetched track is the same as our stored
       * one, we don't want to update the DOM yet.
       */
      if (this.playerResponse.item?.id === this.playerData.trackId) {
        return
      }

      /**
       * Store the current active track.
       */
      this.playerData = {
        playing: this.playerResponse.is_playing,
        trackArtists: this.playerResponse.item.artists.map(
          artist => artist.name
        ),
        trackTitle: this.playerResponse.item.name,
        trackId: this.playerResponse.item.id,
        trackAlbum: {
          title: this.playerResponse.item.album.name,
          image: this.playerResponse.item.album.images[0].url
        }
      }
    },

    /**
     * Handle newly stored colour palette:
     * - Map data to readable format
     * - Get and store random colour combination.
     */
    handleAlbumPalette(palette) {
      let albumColours = Object.keys(palette)
        .filter(item => {
          return item === null ? null : item
        })
        .map(colour => {
          return {
            text: palette[colour].getTitleTextColor(),
            background: palette[colour].getHex()
          }
        })

      this.swatches = albumColours

      this.colourPalette =
        albumColours[Math.floor(Math.random() * albumColours.length)]

      this.$nextTick(() => {
        this.setAppColours()
      })
    },

    /**
     * Handle an expired access token from Spotify.
     */
    handleExpiredToken() {
      clearInterval(this.pollPlaying)
      this.$emit('requestRefreshToken')
    },

    configureMQTT() {
      client.on('connect', function() {
        client.subscribe(TOUCH_INPUT_CHANNEL, function(err) {
          if (!err) {
            console.info(`connected to ${TOUCH_INPUT_CHANNEL}`)
            client.publish('status/client', 'Client connected')
          }
        })
        client.subscribe(SCHEDULE_INPUT_CHANNEL, function(err) {
          if (!err) {
            console.info(`connected to ${SCHEDULE_INPUT_CHANNEL}`)
            client.publish('status/client', 'Client connected')
          }
        })
      })

      client.on('message', function(topic, message) {
        // message is Buffer
        // tap toggles between scheduled position and 100%
        // long press toggles scheduled position and 0%
        console.log(message.toString())
        // handleInput(topic, message)
        if (topic == SCHEDULE_INPUT_CHANNEL) {
          if (this.lastInputType !== LONG_PRESS) {
            this.previousLidPosition = this.currentLidPosition
          }
          this.currentLidPosition = message
          client.publish(LID_POSITION_CHANNEL, `${this.currentLidPosition},${SLOW_SPEED}`)
          this.lastInputType = SCHEDULE
        }
        if (topic == TOUCH_INPUT_CHANNEL) {
          if (message.toString() === TAP) {
            if (this.currentLidPosition === OPEN_100_PERCENT) {
              this.currentLidPosition = this.previousLidPosition
            } else {
              if (this.lastInputType !== LONG_PRESS) {
                this.previousLidPosition = this.currentLidPosition
              }
              this.currentLidPosition = OPEN_100_PERCENT
            }
            client.publish(LID_POSITION_CHANNEL, `${this.currentLidPosition},${MEDIUM_SPEED}`)
            this.lastInputType = TAP
          }
          if (message.toString() === LONG_PRESS) {
            if (this.lastInputType !== LONG_PRESS) {
              this.currentLidPosition = OPEN_0_PERCENT
              client.publish(LID_POSITION_CHANNEL, `${this.currentLidPosition},${SLOW_SPEED}`)
              this.lastInputType = LONG_PRESS
            }
          }
        }
      })
    },
  },
  watch: {
    /**
     * Watch the auth object returned from Spotify.
     */
    auth: function(oldVal, newVal) {
      if (newVal.status === false) {
        clearInterval(this.pollPlaying)
      }
    },

    /**
     * Watch the returned track object.
     */
    playerResponse: function() {
      this.handleNowPlaying()
    },

    /**
     * Watch our locally stored track data.
     */
    playerData: function() {
      this.$emit('spotifyTrackUpdated', this.playerData)
      // this.updateHardwareState(this.playerData.playing)
    }
  }
}
</script>

<style src="@/styles/components/now-playing.scss" lang="scss" scoped></style>

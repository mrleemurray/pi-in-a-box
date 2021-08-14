<template>
  <div>
    
  </div>
</template>

<script>

var weather = require('openweather-apis')

export default {
  name: 'Weather',

  components: {
  },

  props: {},

  data() {
    return {
 
    }
  },

  computed: {},

  created() {
      // set city by name
    weather.setLang('en');
	weather.setCity('Walthamstow')
    weather.setUnits('metric')
    weather.setAPPID(process.env.VUE_APP_OPENWEATHER_APP_ID)
  },

  mounted() {
      // get the Temperature  
	weather.getTemperature(function(err, temp){
		console.log(temp);
	});
    weather.getSmartJSON(function(err, desc){
		console.log(desc);
	});
    weather.getAllWeather(function(err, JSONObj){
		console.log(JSONObj);
	});
    // weather.getWeatherForecastForDays(3, function(err, obj){
	// 	console.log(obj);
	// });
  },

  methods: {

  },

  watch: {
  }
}
</script>

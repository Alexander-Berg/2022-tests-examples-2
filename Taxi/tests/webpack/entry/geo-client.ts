import {geoClient} from '../../../index'

geoClient.getZeroSuggest({
  lang: 'ru',
  location: {
    lat: 0,
    lon: 0,
  },
})

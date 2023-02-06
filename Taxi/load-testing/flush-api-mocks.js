require('dotenv').config()

const { flushAwsRecordings } = require('@lavka-js-toolbox/load-testing')
const { join: joinPath } = require('path')
const config = require(joinPath(process.cwd(), '.load-testing', 'config.js'))

flushAwsRecordings(config).catch(console.error)

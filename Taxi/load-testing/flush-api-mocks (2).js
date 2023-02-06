require('dotenv').config()

const { join: joinPath } = require('path')

const { flushAwsRecordings } = require('@lavka-js-toolbox/load-testing')
const config = require(joinPath(process.cwd(), '.load-testing', 'config.js'))

flushAwsRecordings(config).catch(console.error)

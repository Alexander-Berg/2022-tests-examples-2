const {resolve} = require('path');

require('dotenv').config({path: resolve(__dirname, '../../../.env')});
process.env.__ENVIRONMENT__ = 'jest';

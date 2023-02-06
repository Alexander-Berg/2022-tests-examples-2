const merge = require('lodash/merge');

const commonConfig = require('./testing.common');

let serviceConfig;
try {
    serviceConfig = require(`./testing.${process.env.SERVICE}`);
} catch (e) {}

module.exports = merge({}, commonConfig, serviceConfig);

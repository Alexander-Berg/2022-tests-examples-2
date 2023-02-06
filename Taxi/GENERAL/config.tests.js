const {getBaseConfig} = require('@lavka-birds/tools');
const getPathAliases = require('../get-path-aliases');
const options = require('./config-options');

const alias = getPathAliases();

const baseConfig = getBaseConfig(options);

module.exports = {
    ...baseConfig,
    presets: [['@babel/preset-env', {targets: {node: 'current'}}], ...baseConfig.presets],
    plugins: [['module-resolver', {alias}], ...baseConfig.plugins]
};

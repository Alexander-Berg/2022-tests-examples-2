/* eslint-disable @typescript-eslint/no-var-requires */
const BabelJest = require('babel-jest');
const path = require('path');

const createTransformer = () =>
    BabelJest.createTransformer({
        // Путь к babelrc нужен, чтобы транспилились модули из node_modules,
        // в частности - amber-blocks
        configFile: path.resolve(path.join(__dirname, '..', '..', 'babel.config.js')),
        babelrc: false,
    });
module.exports = createTransformer();
module.exports.createTransformer = createTransformer;

const {nodeResolve} = require('@rollup/plugin-node-resolve'),
    commonjs = require('@rollup/plugin-commonjs'),
    builtins = require('rollup-plugin-node-builtins'),
    globals = require('rollup-plugin-node-globals'),
    path = require('path');

module.exports = {
    input: path.join(__dirname, 'clientEnv.js'),
    context: 'window',
    plugins: [
        nodeResolve({
            browser: true,
            preferBuiltins: true
        }),
        globals({
            process: false,
            buffer: false,
            dirname: false,
            filename: false,
            baseDir: false
        }),
        commonjs({
            ignoreGlobal: true
        }),
        builtins()
    ],
    output: {
        strict: false,
        file: path.join(__dirname, 'clientEnv.bundled.js'),
        name: 'clientEnv',
        format: 'iife'
    }
};

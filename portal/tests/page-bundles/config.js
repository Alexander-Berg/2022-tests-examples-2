const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const {stylesRules, scriptRules} = require('../../rules/loaders');

const browserList = [
    'Safari > 7',
    'Firefox > 27',
    'Chrome >= 21',
    'ie >= 10',
    'edge >= 12',
    'last 2 versions',
    '>1%'
];

const staticPath = '/';

const base = name => {
    return {
        target: 'web',
        mode: 'production',
        module: {
            rules: [
                ...stylesRules({isProd: true, staticPath, browserList}),
                ...scriptRules({isProd: true, staticPath, browserList})
            ]
        },
        output: {
            path: path.resolve(__dirname, name + '/bundles'),
            publicPath: `./${name}/bundles/`
        },
        plugins: [
            new MiniCssExtractPlugin({}),
            new CleanWebpackPlugin()
        ],
        optimization: {
            minimizer: [
                `...`,
                new CssMinimizerPlugin()
            ]
        }
    };
};

module.exports = [
    {
        entry: path.resolve(__dirname, './single-entry/single-entry.js'),
        ...base('single-entry')
    },
    {
        entry: {
            one: path.resolve(__dirname, './multi-entry/multi-entry-1.js'),
            two: path.resolve(__dirname, './multi-entry/multi-entry-2.js'),
            three: path.resolve(__dirname, './multi-entry/multi-entry-3.js'),
            four: path.resolve(__dirname, './multi-entry/multi-entry-4.js'),
            five: path.resolve(__dirname, './multi-entry/multi-entry-5.js')
        },

        ...base('multi-entry')
    }
];

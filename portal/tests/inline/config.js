const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const {stylesRules, scriptRules, svgRules, imgRules} = require('../../rules/loaders');

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

module.exports = {
    target: 'node',
    mode: 'production',
    devtool: false,
    entry: {
        test: path.resolve(__dirname, './entry.js')
    },
    module: {
        rules: [
            ...stylesRules({isProd: true, staticPath, browserList}),
            ...scriptRules({isProd: true, staticPath, browserList}),
            ...svgRules({isProd: true, staticPath}),
            ...imgRules({isProd: true, staticPath}),
        ]
    },
    output: {
        path: path.resolve(__dirname, 'bundles'),
        filename: '[name].js',
        chunkFilename: '[filename].js',
        publicPath: './',
        libraryTarget: 'commonjs2'
    },
    plugins: [
        new MiniCssExtractPlugin({
            chunkFilename: '[contenthash:2]/[contenthash].css'
        })
    ],
    optimization: {
        minimizer: [
            `...`,
            new CssMinimizerPlugin()
        ]
    }
};

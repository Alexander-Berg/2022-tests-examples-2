const path = require('path');
const IE8TemplatePlugin5 = require('../../build-src/IE8-template5');

const base = name => {
    return {
        target: ['node', 'es5'],
        //mode: 'production',
        devtool: false,
        mode: 'development',
        module: {
            rules: [{
                test: /\.js$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', {
                                useBuiltIns: 'usage',
                                corejs: { version: 3, proposals: true },
                                targets: {
                                    ie: 8
                                },
                                modules: false,
                                exclude: [
                                    /^web/,
                                    /^es.typed/,
                                    /^es.regexp/,
                                    /^es.reflect/,
                                    /^es.weak-map/,
                                    /^es.weak-set/,
                                    'transform-async-to-generator',
                                    'transform-regenerator',
                                    'transform-function-name',
                                    // https://github.com/kangax/compat-table/blob/gh-pages/data-es5.js#L777
                                    // (есть бага, что если передали не функцию, то юзается сортировка по умолчанию)
                                    'es.array.sort',
                                ].filter(Boolean)
                            }],
                            '@babel/typescript'
                        ].filter(Boolean)
                    }
                }
            }]
        },
        output: {
            path: path.resolve(__dirname, name + '/bundles'),
            filename: '[name].js',
            publicPath: '/freeze/',
            libraryTarget: 'commonjs2'
        }
    };
};

module.exports = () => {
    return [
        {
            entry: path.resolve(__dirname, './client-side/client-side.js'),
            plugins: [
                new IE8TemplatePlugin5()
            ],
            ...base('client-side')
        }
    ];
};

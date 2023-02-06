const path = require('path');
const LangPlugin = require('../../build-src/LangPlugin');

const base = name => {
    return {
        target: 'node',
        // mode: 'development',
        mode: 'production',
        devtool: false,
        module: {
        },
        output: {
            path: path.resolve(__dirname, name + '/bundles'),
            filename: '[name].js',
            publicPath: '/freeze/',
            libraryTarget: 'commonjs2'
        }
    };
};

module.exports = (translations) => {
    return [
        {
            entry: {
                server: path.resolve(__dirname, './server-side/server-side.js')
            },
            ...base('server-side')
        },
        {
            entry: {
                'client.ru': path.resolve(__dirname, './client-side/client-side.js')
            },
            plugins: [
                new LangPlugin({
                    lang: 'ru',
                    translations,
                    l10nLibMatch: { test: /lib\/home\.l10n\.js$/ },
                    l10nExportMatch: { test: /\.l10n\.js$/, exclude: /lib\/home\.l10n\.js$/ }
                }),
            ],
            ...base('client-side/ru')
        },
        {
            entry: {
                'client.en': path.resolve(__dirname, './client-side/client-side.js')
            },
            plugins: [
                new LangPlugin({
                    lang: 'en',
                    translations,
                    l10nLibMatch: { test: /lib\/home\.l10n\.js$/ },
                    l10nExportMatch: { test: /\.l10n\.js$/, exclude: /lib\/home\.l10n\.js$/ }
                }),
            ],
            ...base('client-side/en')
        }
    ];
};

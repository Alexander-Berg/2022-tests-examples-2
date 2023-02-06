module.exports = {
    target: 'es5',
    mode: 'production',
    entry: {
        desktop: './src/desktop.tsx',
        touch: './src/touch.tsx'
    },
    output: {
        chunkFormat: 'array-push'
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    module: {
        rules: [
            {
                test: /\.[jt]sx?$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', {
                                targets: {
                                    chrome: 42,
                                    firefox: 45,
                                    edge: 12,
                                    ie: 11,
                                    android: '4.4',
                                    ios: 7
                                }
                            }],
                            '@babel/preset-typescript',
                            '@babel/preset-react'
                        ]
                    }
                }
            }
        ]
    }
};

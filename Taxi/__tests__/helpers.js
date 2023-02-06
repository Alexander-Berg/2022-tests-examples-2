const path = require('path');
const webpack = require('webpack');
const MemoryFS = require('memory-fs');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

function compile(entry, baseConfig = {}, options = {}) {
  const css = [
    { loader: path.resolve(__dirname, '../../src/loader.js') },
    { loader: 'style-loader', options: { sourceMap: false, hmr: false } },
    { loader: 'css-loader', options: { sourceMap: false } }
  ];

  const stylus = [
    ...css,
    { loader: 'stylus-loader', options: { sourceMap: false } }
  ];

  const config = {
    ...baseConfig,
    mode: 'development',
    devtool: false,
    entry: path.resolve(__dirname, 'fixtures', entry),
    output: {
      path: path.resolve(__dirname, `outputs`),
      filename: '[name].bundle.js'
    },
    module: {
      rules: []
    },
    plugins: []
  };

  if (options.extractCSS) {
    css[css.findIndex(item => item.loader === 'style-loader')] =
      MiniCssExtractPlugin.loader;

    config.plugins.push(
      new MiniCssExtractPlugin({
        filename: '[name].css',
        chunkFilename: '[name].css'
      })
    );
  }

  config.module.rules.push({ test: /\.css$/, use: css });
  config.module.rules.push({ test: /\.styl$/, use: stylus });

  const compiler = webpack(config);

  if (!options.output) {
    compiler.outputFileSystem = new MemoryFS();
  }

  return new Promise((resolve, reject) =>
    compiler.run((error, stats) => {
      if (error) {
        return reject(error);
      }

      return resolve(stats);
    })
  );
}

module.exports = {
  webpack: compile
};

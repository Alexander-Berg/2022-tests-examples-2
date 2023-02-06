/* eslint-disable */
import path from 'path'
import fs from 'fs'

import TerserPlugin from 'terser-webpack-plugin'
import webpack from 'webpack'

export async function buildWebpack(entryPoint: string) {
  const config: webpack.Configuration = {
    mode: 'production',
    entry: {
      [entryPoint]: path.resolve(__dirname, `entry/${entryPoint}.ts`),
    },
    resolve: {
      extensions: ['.ts', '.js', '.tsx', '.jsx', '.json'],
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          exclude: /node_modules(?!lodash-es)/,
          loader: 'babel-loader',
        },
      ],
    },
    optimization: {
      usedExports: true,
      minimize: true,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            keep_fnames: true,
          },
        }),
      ],
    },
  }

  return new Promise<void>((resolve, reject) => {
    webpack(config, (err, stats) => {
      if (err) {
        reject(err)

        return
      }

      if (stats) {
        const info = stats.toJson()

        if (stats.hasErrors()) {
          console.error(info.errors)

          throw new Error('BUILD_ERROR')
        }

        if (stats.hasWarnings()) {
          console.warn(info.warnings)

          throw new Error('BUILD_ERROR')
        }
      }

      resolve()
    })
  })
}

export async function getWebpackBuildResult(entryPoint: string) {
  await buildWebpack(entryPoint)

  return fs.readFileSync(path.resolve(__dirname, `dist/${entryPoint}.js`), {encoding: 'utf-8'})
}

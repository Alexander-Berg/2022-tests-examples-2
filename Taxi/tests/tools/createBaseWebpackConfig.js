const path = require('path')
const {promisify} = require('util')

const glob = require('glob')
const isBuiltinModule = require('is-builtin-module')
const nodeExternals = require('webpack-node-externals')

const createBaseWebpackConfig = dirname => {
  const isNodeExternals = promisify(
    nodeExternals({
      importType: 'commonjs2',
      additionalModuleDirs: [path.resolve(dirname, '../../../node_modules')],
    }),
  )

  return {
    mode: 'development',
    entry: {
      '.hermione.conf': path.resolve(dirname, './.hermione.conf.ts'),
      ...glob.sync(path.resolve(dirname, './sets/**/*.ts')).reduce((acc, path) => {
        const entry = path.replace(dirname, '').replace('.ts', '')
        console.info('tests file:', entry)
        acc[entry] = path
        return acc
      }, {}),
    },
    target: 'node',
    module: {
      rules: [
        {
          test: /\.ts?$/,
          use: [
            {
              loader: 'ts-loader',
              options: {
                transpileOnly: true,
              },
            },
          ],
          exclude: /node_modules/,
        },
      ],
    },
    resolve: {
      extensions: ['.ts'],
    },
    externals: async ctx => {
      const {request} = ctx

      const isExternals = await isNodeExternals(ctx)

      const isInternalLibrary = request.startsWith('@lavka/')

      if (isExternals && !isInternalLibrary) {
        return isExternals
      }

      if (isBuiltinModule(request)) {
        return
      }
    },
    output: {
      filename: './[name].js',
      libraryTarget: 'commonjs2',
      path: path.resolve(dirname, 'dist'),
    },
  }
}

module.exports = {
  createBaseWebpackConfig,
}

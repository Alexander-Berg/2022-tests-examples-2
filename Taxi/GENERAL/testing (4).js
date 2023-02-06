/*eslint sort-keys: "error"*/
const {getDestinationsInCloud} = require('./tvm')

module.exports = {
  tvm: {
    destinations: getDestinationsInCloud(),
  },
}

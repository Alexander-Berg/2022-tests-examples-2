const _ = require('lodash');
const baseConfig = require('_common/server/configs/testing');
const packageJSON = require('../../package.json');

module.exports = _.merge({}, baseConfig, {
    csp: {
        ...baseConfig.csp,
        policies: {
            ...baseConfig.csp.policies,
            'frame-src': [
                ...baseConfig.csp.policies['frame-src'],
                'secure-me.au10tixservicesstaging.com'
            ]
        },
        serviceName: packageJSON.name
    }
});

const defaults = require('./defaults');

module.exports = {
    csp: {
        policies: {
            ...defaults.csp.policies,
            'script-src': [...(defaults.csp.policies['script-src'] ?? []), 'testing.payment-widget.ott.yandex.ru'],
            'frame-src': [...(defaults.csp.policies['frame-src'] ?? []), 'testing.payment-widget.ott.yandex.ru']
        }
    }
};

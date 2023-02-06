/* eslint-disable */

document = {
    documentElement: {
        style: {}
    },
    implementation: {
        hasFeature: function() {
            return true;
        }
    },
    createElement: function() {
        return {};
    }
};
window = {};
navigator = {
    appName: 'Netscape',
    userAgent: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0'
};
Image = function() {};

var views = home.getView ? home.getView() : null;

/* eslint-enable */

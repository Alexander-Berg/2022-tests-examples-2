/*eslint-disable */
require('chai/chai');
var chai = window.chai;
var chaiAsPromised = require('chai-as-promised');
var sinon = require('sinon/pkg/sinon.js');
var sinonChai = require('sinon-chai');

chai.use(sinonChai);
chai.use(chaiAsPromised);
chai.should();

window.expect = chai.expect;
window.assert = chai.assert;

window.Ya = Window.Ya || {};

window.Ya.Rum = {
    enabled: false,
    getTime: function() {
        return 123;
    },
    logError: console.error
};

window.home = window.home || {};

/**
 * Хелпер для честного создания инстанса BEM.DOM блока
 *
 * @param {Object} bemjson - bemjson блока
 * @param {String} bemjson.block
 * @param {Object} [bemjson.mods]
 * @param {Object} [bemjson.js]
 * @returns {BEM.DOM}
 */
window.buildBlock = function buildBlock (bemjson) {
    var classes = home.getBEMClassname(bemjson.block, bemjson),
        js = {},
        params = '';

    if (bemjson.js && typeof bemjson.js === 'object') {
        js[bemjson.block] = bemjson.js;
        params = home.getBEMParams(js);
    }

    var html = '<div class="${classes}" data-bem="${params}"></div>'
        .replace('${classes}', classes)
        .replace('${params}', params);

    return BEM.DOM.init(html).appendTo(BEM.DOM.scope).bem(bemjson.block);
};

/*eslint-enable */

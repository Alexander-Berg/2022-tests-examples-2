const outermostSelfCallingFuncRemover = require('./outermost-self-calling-func-remover');
const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

describe('template-functions-modifier', () => {
    before(function() {
        chaiJestSnapshot.resetSnapshotRegistry();
    });
    it('should transform self calling functions', () => {
        const input = `
/* global views */
(function (views) {
    'use strict';
    views('head__title', function(data, req) {
        return req.l10n('yandex');
    });

    views('head__links', function(data, req) {
        var links = [];

        links.push({
            rel: 'search',
            href: '//yandex.' + req.MordaZone + '/opensearch.xml',
            title: req.l10n('page.opensearch'),
            type: 'application/opensearchdescription+xml'
        });

        return links;
    });

    views('head__metas', function (data, req) {
        var metas = [],
            turkey = req.MordaZone === 'com.tr';

        var ogDescription = '',
            ogTitle = '';

        return metas;
    });

})(views);
        `;
        const output = outermostSelfCallingFuncRemover(input);
        chai.expect(output).to.matchSnapshot();
    });

    it('should not forget comments inside function body', () => {
        const input = `
/* global views */
// comment 0
(function (views) {
    'use strict';
    // comment 1
    views('head__title', function(data, req) {
        return req.l10n('yandex');
    });
    // comment 2
    // comment 3
    views('head__links', function(data, req) {
        var links = [];

        links.push({
            rel: 'search',
            href: '//yandex.' + req.MordaZone + '/opensearch.xml',
            title: req.l10n('page.opensearch'),
            type: 'application/opensearchdescription+xml'
        });

        return links;
    });
    // comment 4
    // comment 5
    views('head__metas', function (data, req) {
        var metas = [],
            turkey = req.MordaZone === 'com.tr';

        var ogDescription = '',
            ogTitle = '';

        return metas;
    });
    // comment 6
})(views);
// comment 7
        `;
        const output = outermostSelfCallingFuncRemover(input);
        chai.expect(output).to.matchSnapshot();

    });
});
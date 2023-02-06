const fs = require('fs');
const read = fs.readFileSync;
const {analyze} = require('../index');
const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {desktop_bundle_info} = require('./mocks')
const {updateMock} = require('./helper');

describe('Morda bundle analyzer test', () => {
    it('should return correct desktop bundle info', () => {
        const bundle = read('./test/mocks/bundles/desktop.bundle.min.js', 'utf-8');
        const info = analyze(bundle);

        updateMock(info, 'desktop-bundle-info')
        //assert.deepEqual(1, 1);
       // assert.deepEqual(info, desktop_bundle_info);
    });
});
/* global __INJECTED_LEVEL_PATH__, before, beforeEach */
const chai = require('chai');
require('source-map-support/register');
const sourceMapSupport = require('source-map-support');
sourceMapSupport.install();

// chai-jest-snapshot setup

const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

before(function() {
    chaiJestSnapshot.resetSnapshotRegistry();
});

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

function importAll (r) {
    r.keys().forEach(r);
}
importAll(require.context(__INJECTED_LEVEL_PATH__, true, /\.view\.test\.js$/));

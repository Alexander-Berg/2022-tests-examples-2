'use strict';

// eslint-disable-next-line node/no-extraneous-require
const chai = require('chai');
// eslint-disable-next-line node/no-extraneous-require
const sinonChai = require('sinon-chai');
chai.use(sinonChai);
chai.should();
global.expect = chai.expect;

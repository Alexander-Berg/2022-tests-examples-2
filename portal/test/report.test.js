const fs = require('fs');
const {getReportByTags} = require('../index');
const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {desktop_bundle_info} = require('./mocks')
const {updateMock} = require('./helper');

describe.only('Morda bundle reporter test', () => {
    it('should return json reported', () => {
        getReportByTags('2020-05-30-0');
    });
});
const supertest = require('supertest');
const app = require('../../../../app.js');
const request = supertest(app);
const routeUrl = '/auth/sso/commit';
const {
    headers,
    basic: {trackID}
} = require('../../../util/mock/mockData.js');

require('../../../util/mock/mockApi.js');

describe(`POST ${routeUrl}`, function() {
    it('returns 302 if everything is ok', function(done) {
        request
            .post(routeUrl)
            .type('form')
            .set(headers)
            .send({
                SAMLResponse: '1111',
                RelayState: '2222'
            })
            .expect('Location', new RegExp(`/auth/session\\?track_id=${trackID}`, 'g'))
            .expect(302, done);
    });

    //    it('returns 200 and error code if something is wrong 1', function(done) {
    //        request
    //            .post(routeUrl)
    //            .type('form')
    //            .set(headers)
    //            .send({
    //                SAMLResponse: '0000',
    //                RelayState: '2222'
    //            })
    //            .expect(200)
    //            .expect(new RegExp(`samlresponse.invalid`), done);
    //    });
    //
    //    it('returns 200 and error code if something is wrong 2', function(done) {
    //        request
    //            .post(routeUrl)
    //            .type('form')
    //            .set(headers)
    //            .send({
    //                SAMLResponse: '2222',
    //                RelayState: '2222'
    //            })
    //            .expect(200)
    //            .expect(new RegExp(`saml_settings.invalid`), done);
    //    });

    it('returns 500 if required params are missing', function(done) {
        request
            .post(routeUrl)
            .type('form')
            .set(headers)
            .send({
                SAMLResponse: '1111'
            })
            .expect(500)
            .expect(new RegExp(`["required_params.missing"]`), done);
    });

    it('returns 500 if required params are missing', function(done) {
        request
            .post(routeUrl)
            .type('form')
            .set(headers)
            .send({
                RelayState: '2222'
            })
            .expect(500)
            .expect(new RegExp(`["required_params.missing"]`), done);
    });
});

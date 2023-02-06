const chai = require('chai');

describe('Hermione test', function () {
    const protocol = 'http';
    const { domain, port } = hermione.ctx;
    const baseUrl = `${protocol}://${domain}${
        port ? `:${port}` : ''
    }/test/hermione/hermione.hbs`;
    it('should find hermione', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect('Hermione page').to.be.equal(innerText);
            });
    });
});

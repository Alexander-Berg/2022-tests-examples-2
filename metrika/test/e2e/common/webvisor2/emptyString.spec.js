const chai = require('chai');
const { findNodeBySnapshot, findNodeWithAttribute } = require('./utils');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    it('Protobuf correctly encodes empty strings', function () {
        const emptyString = '';
        const nullString = String.fromCharCode(0);

        return this.browser
            .timeoutsAsyncScript(5000)
            .url('test/webvisor2/emptyString.hbs')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        /*
                         * Have to collect requests manually and then send them stringified
                         * cause hermione will trim out the null chars.
                         * For the same reason "nullString" shall not be passed here as a parameter.
                         */
                        window.requests = [];
                        window._socket.on('request', function (r) {
                            window.requests.push(r);
                        });

                        document
                            .querySelector('#with-empty-content')
                            .appendChild(document.createTextNode(''));
                        document
                            .querySelector('#with-null-content')
                            .appendChild(
                                document.createTextNode(String.fromCharCode(0)),
                            );
                        document
                            .querySelector('#with-null-attribute')
                            .setAttribute('data-empty', String.fromCharCode(0));

                        new Ya.Metrika2({ id: 123, webvisor: true });
                        done(true);
                    },
                }),
            )
            .pause(4000)
            .execute(() => JSON.stringify(window.requests))
            .then((info) => ({
                ...info,
                value: JSON.parse(info.value),
            }))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const page = visorData.find((item) => item.type === 'page');
                chai.expect(page, 'page').to.be.ok;

                const nodeWithEmptyContent = findNodeWithAttribute(
                    page,
                    'with-empty-content',
                );
                chai.expect(nodeWithEmptyContent).to.be.ok;
                const emptyTextNode = findNodeBySnapshot(page, {
                    parent: nodeWithEmptyContent.id,
                });
                chai.expect(emptyTextNode).to.be.ok;
                chai.assert(
                    emptyTextNode.content === emptyString,
                    'Empty string node content',
                );

                const nodeWithNullContent = findNodeWithAttribute(
                    page,
                    'with-null-content',
                );
                chai.expect(nodeWithNullContent).to.be.ok;
                const nullTextNode = findNodeBySnapshot(page, {
                    parent: nodeWithNullContent.id,
                });
                chai.expect(nullTextNode).to.be.ok;
                chai.assert(
                    nullTextNode.content === nullString,
                    'Null string node content',
                );

                const nodeWithEmptyAttribute = findNodeWithAttribute(
                    page,
                    'with-empty-attribute',
                );
                chai.expect(nodeWithEmptyAttribute).to.be.ok;
                chai.assert(
                    nodeWithEmptyAttribute.attributes['data-empty'] ===
                        emptyString,
                    'Empty node attribute',
                );

                const nodeWithNullAttribute = findNodeWithAttribute(
                    page,
                    'with-null-attribute',
                );
                chai.expect(nodeWithNullAttribute).to.be.ok;
                chai.assert(
                    nodeWithNullAttribute.attributes['data-empty'] ===
                        nullString,
                    'Node attribute with null char',
                );
            });
    });
});

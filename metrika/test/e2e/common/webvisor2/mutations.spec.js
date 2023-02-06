const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { findNodeWithAttribute } = require('./utils');

describe('webvisor2', function () {
    const baseUrl = 'test/webvisor2/';
    const counterId = 403928;
    const checkMutations = (browser, isProto = false) => {
        return browser
            .url(`${baseUrl}mutations.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Mutations page');
            })
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options) {
                        if (options.isProto) {
                            document.cookie = '_ym_debug=""';
                        }
                        window.req = [];
                        serverHelpers.collectRequestsForTime(6000, 'webvisor');
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                        setTimeout(() => {
                            document.querySelector('#button').click();
                        }, 500);
                    },
                    isProto,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const page = visorData.find((event) => event.type === 'page');
                const mutations = visorData.filter(
                    (event) => event.type === 'mutation',
                );
                const containerId = findNodeWithAttribute(page, 'container').id;
                const parsedMutations = mutations.reduce((result, mutation) => {
                    const { stamp } = mutation;
                    const { index } = mutation.data;
                    const { changes } = mutation.data.meta;
                    chai.expect(
                        changes.length,
                        'only one change per mutation (old format garbage legacy)',
                    ).to.equal(1);
                    const { a, b, c, d } = changes[0];
                    chai.expect(
                        [a, b, c, d].reduce(
                            (prev, next) => prev + (next ? 1 : 0),
                            0,
                        ),
                        'only one type of change in one change record (old format garbage legacy)',
                    ).to.equal(1);
                    if (a) {
                        // Removal
                        a.forEach((change) => {
                            result.push({
                                index,
                                stamp,
                                id: change.id,
                                type: 'remove',
                            });
                        });
                    } else if (b) {
                        // Addition
                        b.forEach((node) => {
                            result.push({
                                ...node,
                                stamp,
                                index,
                                type: 'add',
                            });
                        });
                    } else if (c) {
                        // Attribute change
                        c.forEach((change) => {
                            result.push({
                                ...change,
                                index,
                                stamp,
                                type: 'attr',
                            });
                        });
                    } else if (d) {
                        // Text change
                        d.forEach((change) => {
                            result.push({
                                ...change,
                                index,
                                stamp,
                                type: 'content',
                            });
                        });
                    }

                    return result;
                }, []);

                const checkNodeAdd = (
                    node,
                    parentId,
                    name,
                    attributes,
                    prevId,
                    nextId,
                    content,
                ) => {
                    chai.expect(node.type, 'should be add event').to.equal(
                        'add',
                    );
                    chai.expect(node.pa, 'should have correct parent').to.equal(
                        parentId,
                    );
                    chai.expect(node.nm, 'should have correct name').to.equal(
                        name,
                    );
                    if (attributes) {
                        chai.expect(
                            node.at,
                            'attributes are correct',
                        ).to.deep.equal(attributes);
                    }
                    if (prevId) {
                        chai.expect(
                            node.pr,
                            'should have correct prev reference',
                        ).to.equal(prevId);
                    }
                    if (nextId) {
                        chai.expect(
                            node.nx,
                            'should have correct next reference',
                        ).to.equal(nextId);
                    }
                    if (content) {
                        chai.expect(
                            node.ct,
                            'should have correct content',
                        ).to.equal(content);
                    }
                };
                const [
                    spicyNodeAdd,
                    afterNodeAdd,
                    mutaingNodeAdd,
                    innerTextAdd,
                    innerTextChange,
                    attributeChange,
                    nodeRemoval,
                    nodeReincertion,
                    textNodeReincertion,
                ] = parsedMutations;

                checkNodeAdd(spicyNodeAdd, containerId, 'script', {
                    id: 'spicy',
                    normalattribute: 'normalValue',
                });
                checkNodeAdd(afterNodeAdd, containerId, 'div', {
                    id: 'afterNode',
                });
                checkNodeAdd(
                    mutaingNodeAdd,
                    containerId,
                    'div',
                    {
                        id: 'changed',
                        attr: 'val',
                    },
                    spicyNodeAdd.id,
                    afterNodeAdd.id,
                );
                checkNodeAdd(
                    innerTextAdd,
                    mutaingNodeAdd.id,
                    '#text',
                    null,
                    null,
                    null,
                    'Some text',
                );

                chai.expect(
                    innerTextChange.type,
                    'has change text event',
                ).to.equal('content');
                chai.expect(
                    innerTextChange.id,
                    'changed text on the correct node',
                ).to.equal(innerTextAdd.id);
                chai.expect(
                    innerTextChange.ct.n,
                    'has correct text content',
                ).to.equal('Some changed text');

                chai.expect(
                    attributeChange.type,
                    'has attr change event',
                ).to.equal('attr');
                chai.expect(
                    attributeChange.at.attr.n,
                    'has correct attr value',
                ).to.equal('val1');
                chai.expect(
                    attributeChange.id,
                    'attr changed on the correct node',
                ).to.equal(mutaingNodeAdd.id);

                chai.expect(
                    nodeRemoval.type,
                    'has node removal event',
                ).to.equal('remove');
                chai.expect(nodeRemoval.id, 'correct node removed').to.equal(
                    mutaingNodeAdd.id,
                );

                checkNodeAdd(nodeReincertion, containerId, 'div', {
                    attr: 'val1',
                    id: 'changed',
                });
                checkNodeAdd(
                    textNodeReincertion,
                    nodeReincertion.id,
                    '#text',
                    null,
                    null,
                    null,
                    'Some changed text',
                );
            });
    };

    it('sends mutations (json)', function () {
        return checkMutations(this.browser, false);
    });

    it('sends mutations (proto)', function () {
        return checkMutations(this.browser, true);
    });
});

const chai = require('chai');
const { findNodeWithAttribute } = require('./utils');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    const baseUrl = 'test/webvisor2/';
    const counterId = 45329;

    const checkVisorData = (visorData) => {
        const page = visorData.find(
            ({ type, data }) => type === 'page' && !data.frameId,
        );
        const events = visorData.filter(({ type }) => type === 'event');
        const mutations = visorData.filter(({ type }) => type === 'mutation');
        chai.expect(page, 'page').to.be.ok;

        const removedNodeId = findNodeWithAttribute(page, 'remove').id;
        const changedNodeId = findNodeWithAttribute(page, 'change').id;
        const textContentChangedNodeId = page.data.content.find(
            (nodeInfo) => nodeInfo.parent === changedNodeId,
        ).id;
        const inputNodeId = page.data.content.find(
            (nodeInfo) => (nodeInfo.attributes || {}).id === 'input',
        ).id;
        const passwordNodeId = page.data.content.find(
            (nodeInfo) => (nodeInfo.attributes || {}).id === 'password',
        ).id;
        const containerNodeId = page.data.content.find(
            (nodeInfo) => (nodeInfo.attributes || {}).id === 'container',
        ).id;

        chai.expect(passwordNodeId, 'passwordNodeId').to.be.ok;
        chai.expect(removedNodeId, 'removedNodeId').to.be.ok;
        chai.expect(changedNodeId, 'changedNodeId').to.be.ok;
        chai.expect(textContentChangedNodeId, 'textContentChangedNodeId').to.be
            .ok;
        chai.expect(inputNodeId, 'inputNodeId').to.be.ok;
        chai.expect(containerNodeId, 'containerNodeId').to.be.ok;

        const initialResize = events.find(
            (event) => event.data.type === 'resize',
        );
        chai.expect(initialResize.stamp, 'initialResize.stamp').to.equal(0);
        chai.expect(
            initialResize.data.meta.width,
            'initialResize.data.meta.width',
        ).not.NaN;
        chai.expect(
            initialResize.data.meta.height,
            'initialResize.data.meta.height',
        ).not.NaN;
        chai.expect(
            initialResize.data.meta.pageWidth,
            'initialResize.data.meta.pageWidth',
        ).not.NaN;
        chai.expect(
            initialResize.data.meta.pageHeight,
            'initialResize.data.meta.pageHeight',
        ).not.NaN;

        const initialScroll = events.find(
            (event) => event.data.type === 'scroll',
        );
        chai.expect(initialScroll.stamp, 'initialScroll.stamp').to.equal(0);
        chai.assert(
            initialScroll.data.meta.y === 0,
            'initialScroll.data.meta.y',
        );
        chai.assert(
            initialScroll.data.meta.x === 0,
            'initialScroll.data.meta.x',
        );
        chai.assert(
            initialScroll.data.meta.page,
            'initialScroll.data.meta.page',
        );

        // Input value
        const valueChange = events.find(
            (event) =>
                event.data.type === 'change' &&
                event.data.target === inputNodeId,
        );
        chai.expect(valueChange, 'valueChnage').to.be.ok;
        chai.expect(valueChange.stamp, 'valueChange.stamp').not.NaN;
        chai.assert(
            valueChange.data.meta.value === '666',
            'valueChange.data.meta.value',
        );
        chai.assert(
            !valueChange.data.meta.hidden,
            'valueChange.data.meta.hidden',
        );

        // Password value and attribute
        const passwordChange = events.find(
            (event) =>
                event.data.type === 'change' &&
                event.data.target === passwordNodeId,
        );
        chai.expect(passwordChange, 'passwordChange').to.be.ok;
        chai.expect(passwordChange.stamp, 'passwordChange.stamp').not.NaN;
        chai.assert(
            passwordChange.data.meta.value === '•••',
            'passwordChange.data.meta.value',
        );
        chai.assert(
            passwordChange.data.meta.hidden,
            'passwordChange.data.meta.hidden',
        );

        const passwordChangeMutation = mutations.find((mutation) => {
            const change = mutation.data.meta.changes[0].c;
            return change && change[0].id === passwordNodeId;
        }).data.meta.changes[0].c[0];
        chai.expect(passwordChangeMutation, 'passwordChangeMutation').to.be.ok;
        chai.expect(
            passwordChangeMutation.at.value.n,
            'attributeChangeMutation.at.value.n',
        ).to.equal('•••');

        // Text content
        const textContentChangeMutation = mutations.find((mutation) => {
            return mutation.data.meta.changes[0].d;
        }).data.meta.changes[0].d[0];
        chai.expect(
            textContentChangeMutation.id,
            'textContentChangeMutation.id',
        ).to.equal(textContentChangedNodeId);
        chai.expect(
            textContentChangeMutation.ct.n,
            'textContentChangeMutation.ct.n',
        ).to.equal('new text content');

        // Attribute change
        const attributeChangeMutation = mutations.find((mutation) => {
            const change = mutation.data.meta.changes[0].c;
            return change && change[0].id === changedNodeId;
        }).data.meta.changes[0].c[0];
        chai.expect(
            attributeChangeMutation.at.attr1.n,
            'attributeChangeMutation.at.attr1.n',
        ).to.equal('123');

        // Node add
        const addedNodeMutation = mutations.reverse().find((mutation) => {
            return mutation.data.meta.changes[0].b;
        }).data.meta.changes[0].b[0];
        chai.expect(addedNodeMutation.nm, 'addedNodeMutation.nm').to.equal(
            'div',
        );
        chai.expect(
            addedNodeMutation.at.id,
            'addedNodeMutation.at.id',
        ).to.equal('added-node');
        chai.expect(addedNodeMutation.pa, 'addedNodeMutation.pa').to.equal(
            containerNodeId,
        );

        chai.assert(
            mutations.some((mutation) => {
                return (
                    mutation.data.meta.changes[0].a &&
                    mutation.data.meta.changes[0].a[0].id === removedNodeId
                );
            }),
            'mutation.data.meta.changes[0].a[0].id',
        );
    };

    function checkMutationsAndEvents(isProto) {
        return this.browser
            .timeoutsAsyncScript(5000)
            .url(`${baseUrl}webvisor2.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        if (options.isProto) {
                            document.cookie = '_ym_debug=""';
                        }

                        serverHelpers.collectRequestsForTime(4000, 'webvisor');
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });

                        setTimeout(() => {
                            document.querySelector('#button').click();
                        }, 1000);
                    },
                    counterId,
                    isProto,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then(checkVisorData);
    }

    function checkBigPages(isProto) {
        return this.browser
            .timeoutsAsyncScript(15000)
            .url(
                `${baseUrl}webvisor2-chunk.hbs?${isProto ? '' : '_ym_debug=1'}`,
            )
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Chunk page');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        if (options.isProto) {
                            document.cookie = '_ym_debug=""';
                        }
                        serverHelpers.collectRequests(
                            2000,
                            done,
                            options.regexp.webvisorRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                    },
                    counterId,
                    isProto,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const reqInfo = requests.map(e2eUtils.getRequestParams);
                const bodies = reqInfo.flatMap((info) => info.body);

                const chunks = bodies.filter((info) => {
                    return info.type === 'chunk';
                });

                const parts = chunks.map((info) => {
                    return info.partNum;
                });

                chai.expect(parts).to.include.all.members([1, 2, 3]);

                chai.expect(chunks).to.be.lengthOf(3);
                const hasEnd = chunks.some((info) => {
                    return info.end;
                });
                chai.expect(hasEnd).to.be.ok;
            });
    }
    it('stops if sampling', function () {
        return this.browser
            .url(`${baseUrl}webvisor2-chunk.hbs`)
            .deleteCookie('_ym_visorc')
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Chunk page');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        webvisor: {
                                            recp: '0.0000',
                                        },
                                    },
                                },
                                count: 1,
                            },
                            function () {
                                serverHelpers.collectRequests(
                                    2000,
                                    done,
                                    options.regexp.webvisorRequestRegEx,
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                    webvisor: true,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests).lengthOf(0);
            });
    });

    it('Records big pages (json)', function () {
        return checkBigPages.call(this, false);
    });

    it('Records big pages (proto)', function () {
        return checkBigPages.call(this, true);
    });

    it('Records events and mutations (json)', function () {
        return checkMutationsAndEvents.call(this, false);
    });

    it('Records events and mutations (proto)', function () {
        return checkMutationsAndEvents.call(this, true);
    });
});

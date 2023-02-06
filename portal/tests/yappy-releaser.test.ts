import {expect} from 'chai';
import chai from 'chai';
import sinonChai from 'sinon-chai';
import {YappyReleaser} from '../lib/yappy-releaser';
import {
    getComponentMock,
    getWorkflowMock,
    getGraphMock,
    getSandboxMock,
    getYappyMock,
    getResourceMock,
    getIssueProviderMock
} from './mocks';

chai.use(sinonChai);

describe('yappy-releaser', function () {
    let workflowMock,
        sandboxMock,
        yappyMock,
        graphMock,
        addStepSpy;

    process.env.TRENDBOX_SYNCHROPHAZOTRON = 'TRENDBOX_SYNCHROPHAZOTRON';

    const resourcesMock = {
        logs: getResourceMock({}),
        foo: getResourceMock({
            type: 'TYPE_FOO',
            attributes: {
                version: '123'
            }
        }),
        'no-changes': getResourceMock({
            type: 'TYPE_NO-CHANGES',
            attributes: {
                version: '123'
            }
        }),
        'have-changes': getResourceMock({
            type: 'TYPE_HAVE-CHANGES',
            attributes: {
                version: '123'
            }
        })
    };

    beforeEach(() => {
        workflowMock = getWorkflowMock();
        sandboxMock = getSandboxMock();
        graphMock = getGraphMock();
        yappyMock = getYappyMock();

        workflowMock.getTicket.returns(getIssueProviderMock());

        sandboxMock.getReleaseResources.resolves([
            resourcesMock.foo,
            resourcesMock.logs,
            resourcesMock['no-changes']
        ]);

        addStepSpy = graphMock.addStep;
    });


    describe('не вызывает пересборку', () => {
        it('если нет компонентов', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                suffix: 'qwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                components: [],
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_123'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });

        it('если среди компонентов нет подходящих', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                suffix: 'qwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ],
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_123'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });

        it('если среди компонентов нет подходящих + forceRebuild', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                suffix: 'qwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                forceRebuild: true,
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ],
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_123'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });
    });

    describe('вызывает пересборку компонента', () => {
        it('если есть компонент с изменениями', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('have-changes', true, true),
                    getComponentMock('have-changes-2', true, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                suffix: 'qweqwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_FOO'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_HAVE-CHANGES'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_NO-CHANGES'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.deep.equal(['have-changes', 'foo']);
        });

        it('если изменений нет, но есть forceRebuild', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                forceRebuild: true,
                suffix: 'qweqwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_FOO'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_HAVE-CHANGES'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_NO-CHANGES'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.deep.equal(['no-changes', 'foo']);
        });
    });

    describe('не добавляет шаги деплоя', () => {
        it('если нет компонентов', async () => {
            const releaser = new YappyReleaser({
                suffix: 'qwe',
                project: 'test',
                prevVersion: '123',
                version: '125',
                readinessTimeout: 5,
                templateName: 'test-template',
                components: [],
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_123'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            await releaser.fillGraph(new Set(['qwe']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если среди компонентов нет подходящих', async () => {
            const releaser = new YappyReleaser({
                suffix: 'qwe',
                project: 'test',
                prevVersion: '123',
                version: '125',
                readinessTimeout: 5,
                templateName: 'test-template',
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ],
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_123'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            await releaser.fillGraph(new Set(['foo', 'null']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если среди компонентов нет подходящих + forceRebuild', async () => {
            const releaser = new YappyReleaser({
                suffix: 'qwe',
                project: 'test',
                prevVersion: '123',
                version: '125',
                forceRebuild: true,
                readinessTimeout: 5,
                templateName: 'test-template',
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ],
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_123'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            await releaser.fillGraph(new Set(['foo', 'null']), graphMock);

            addStepSpy.should.not.been.called;
        });
    });

    describe('добавляет шаги деплоя', () => {
        it('если есть компонент с изменениями', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('have-changes', true, true),
                    getComponentMock('have-changes-2', true, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                suffix: 'qweqwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_FOO'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_HAVE-CHANGES'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_NO-CHANGES'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            await releaser.fillGraph(new Set(['have-changes', 'foo', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.called;

            const calls = addStepSpy.getCalls();

            calls.should.have.lengthOf(4, calls);

            [
                'have-changes',
                'foo'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name]);

                call.should.have.property('name')
                    .which.equals('pack-TYPE_' + name.toUpperCase());

                call.should.have.property('isDeploy')
                    .which.equals(false);
            });

            const call = calls[2].firstArg;

            call.should.have.property('deps')
                .which.deep.equal(['pack-TYPE_HAVE-CHANGES', 'pack-TYPE_FOO']);

            call.should.have.property('name')
                .which.equals('yappy-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const waiter = calls[3].firstArg;

            waiter.should.have.property('deps')
                .which.deep.equal(['yappy-deploy']);

            waiter.should.have.property('name')
                .which.equals('yappy-wait');

            waiter.should.have.property('isDeploy')
                .which.equals(false);
        });

        it('если изменений нет, но есть forceRebuild', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                forceRebuild: true,
                suffix: 'qweqwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_FOO'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_HAVE-CHANGES'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_NO-CHANGES'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            await releaser.fillGraph(new Set(['no-changes', 'foo', 'null', 'qwe']), graphMock);

            const calls = addStepSpy.getCalls();

            calls.should.have.lengthOf(4, calls);

            [
                'no-changes',
                'foo'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('name')
                    .which.equals('pack-TYPE_' + name.toUpperCase());

                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name], `${name} deps`);

                call.should.have.property('isDeploy')
                    .which.equals(false);
            });

            const call = calls[2].firstArg;

            call.should.have.property('deps')
                .which.deep.equal(['pack-TYPE_NO-CHANGES', 'pack-TYPE_FOO'], 'nanny deps');

            call.should.have.property('name')
                .which.equals('yappy-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const waiter = calls[3].firstArg;

            waiter.should.have.property('deps')
                .which.deep.equal(['yappy-deploy']);

            waiter.should.have.property('name')
                .which.equals('yappy-wait');

            waiter.should.have.property('isDeploy')
                .which.equals(false);
        });

        it('если изменений нет, но компонент в списке', async () => {
            const releaser = new YappyReleaser({
                project: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                suffix: 'qweqwe',
                templateName: 'test-template',
                readinessTimeout: 5,
                patches: [{
                    componentId: 'tmpl1',
                    parentExternalId: 'test',
                    resources: [{
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_FOO'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_HAVE-CHANGES'
                    },
                    {
                        manageType: 'SANDBOX_RESOURCE',
                        localPath: 'test',
                        sandboxResourceType: 'TYPE_NO-CHANGES'
                    }]
                }]
            }, {
                workflow: workflowMock,
                sandbox: sandboxMock,
                yappy: yappyMock
            });

            await releaser.fillGraph(new Set(['no-changes', 'foo', 'null', 'qwe']), graphMock);

            const calls = addStepSpy.getCalls();

            calls.should.have.lengthOf(4, calls);

            [
                'no-changes',
                'foo'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('name')
                    .which.equals('pack-TYPE_' + name.toUpperCase());

                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name], `${name} deps`);

                call.should.have.property('isDeploy')
                    .which.equals(false);
            });

            const call = calls[2].firstArg;

            call.should.have.property('deps')
                .which.deep.equal(['pack-TYPE_NO-CHANGES', 'pack-TYPE_FOO'], 'nanny deps');

            call.should.have.property('name')
                .which.equals('yappy-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const waiter = calls[3].firstArg;

            waiter.should.have.property('deps')
                .which.deep.equal(['yappy-deploy']);

            waiter.should.have.property('name')
                .which.equals('yappy-wait');

            waiter.should.have.property('isDeploy')
                .which.equals(false);
        });
    });
});

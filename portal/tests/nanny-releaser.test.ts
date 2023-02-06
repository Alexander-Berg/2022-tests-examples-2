import chai from 'chai';
import {expect} from 'chai';
import sinonChai from 'sinon-chai';
import {NannyReleaser} from '../lib/nanny-releaser';
import {
    getComponentMock,
    getWorkflowMock,
    getGraphMock,
    getSandboxMock,
    getResourceMock,
    getIssueProviderMock
} from './mocks';

chai.use(sinonChai);


describe('nanny-releaser', () => {
    let workflowMock,
        sandboxMock,
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
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: []
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });

        it('если среди компонентов нет подходящих', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });

        it('если среди компонентов нет подходящих + forceRebuild', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                forceRebuild: true,
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });

        it('если у компонентов нет изменений и ресурсы есть в предыдущем няня-релизе', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, true),
                    getComponentMock('foo', false, true, false),
                    getComponentMock('null', false, false, true)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.be.empty;
        });
    });


    describe('не добавляет шаги для деплоя', () => {
        it('если нет компонентов', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: []
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['foo']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если среди компонентов нет подходящих', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['qwe']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если среди компонентов нет подходящих + forceRebuild', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                forceRebuild: true,
                components: [
                    getComponentMock('foo', true, false),
                    getComponentMock('null', false, false)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['qwe']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если у компонентов нет изменений и ресурсы есть в предыдущем няня-релизе', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, true),
                    getComponentMock('foo', false, true, false),
                    getComponentMock('null', false, false, true)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['qwe']), graphMock);

            addStepSpy.should.not.been.called;
        });
    });

    describe('вызывает пересборку компонента', () => {
        it('если есть компонент с изменениями', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('have-changes', true, true),
                    getComponentMock('have-changes-2', true, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.deep.equal(['have-changes', 'foo']);
        });

        it('если изменений нет, но есть forceRebuild', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                forceRebuild: true
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.deep.equal(['no-changes', 'foo']);
        });

        it('если изменений нет, но в предыдущем няня-релизе нет нужного ресурса', async () => {
            sandboxMock.getReleaseResources.reset();
            sandboxMock.getReleaseResources.resolves([
                resourcesMock.foo,
                resourcesMock.logs
            ]);

            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, true),
                    getComponentMock('foo', false, true, false),
                    getComponentMock('null', false, false, true)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            const names = await releaser.getComponentsToRebuild();
            expect(names).to.deep.equal(['no-changes']);
        });
    });


    describe('добавляет шаги для деплоя', () => {
        it('если есть компонент с изменениями', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('have-changes', true, true),
                    getComponentMock('have-changes-2', true, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['have-changes', 'foo', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledThrice;

            const calls = addStepSpy.getCalls();

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
                .which.equals('nanny-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const cmd = call.step;
            cmd.should.include('TYPE_FOO@125');
            cmd.should.include('TYPE_HAVE-CHANGES@125');
        });

        it('если изменений нет, но есть forceRebuild', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                forceRebuild: true
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['no-changes', 'foo', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledThrice;

            const calls = addStepSpy.getCalls();

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
                .which.equals('nanny-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const cmd = call.step;
            cmd.should.include('TYPE_FOO@125');
            cmd.should.include('TYPE_NO-CHANGES@125');
        });

        it('если изменений нет, но в предыдущем няня-релизе нет нужного ресурса', async () => {
            sandboxMock.getReleaseResources.reset();
            sandboxMock.getReleaseResources.resolves([
                resourcesMock.foo,
                resourcesMock.logs
            ]);

            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, true),
                    getComponentMock('foo', false, true, false),
                    getComponentMock('null', false, false, true)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['no-changes', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledTwice;

            const calls = addStepSpy.getCalls();

            [
                'no-changes'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('name')
                    .which.equals('pack-TYPE_' + name.toUpperCase());

                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name], `${name} deps`);

                call.should.have.property('isDeploy')
                    .which.equals(false);
            });

            const call = calls[1].firstArg;

            call.should.have.property('deps')
                .which.deep.equal(['pack-TYPE_NO-CHANGES'], 'nanny deps');

            call.should.have.property('name')
                .which.equals('nanny-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const cmd = call.step;
            cmd.should.include('TYPE_FOO@123');
            cmd.should.include('TYPE_NO-CHANGES@125');
        });

        it('если изменений нет, но компонент есть в списке пересобираемых', async () => {
            const releaser = new NannyReleaser({
                project: 'test',
                owner: 'test',
                prevVersion: '123',
                version: '125',
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, true),
                    getComponentMock('foo', false, true, false),
                    getComponentMock('null', false, false, true)
                ]
            }, {
                workflow: workflowMock,
                sandboxApi: sandboxMock
            });

            await releaser.fillGraph(new Set(['no-changes', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledTwice;

            const calls = addStepSpy.getCalls();

            [
                'no-changes'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('name')
                    .which.equals('pack-TYPE_' + name.toUpperCase());

                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name], `${name} deps`);

                call.should.have.property('isDeploy')
                    .which.equals(false);
            });

            const call = calls[1].firstArg;

            call.should.have.property('deps')
                .which.deep.equal(['pack-TYPE_NO-CHANGES'], 'nanny deps');

            call.should.have.property('name')
                .which.equals('nanny-deploy');

            call.should.have.property('isDeploy')
                .which.equals(true);

            const cmd = call.step;
            cmd.should.include('TYPE_FOO@123');
            cmd.should.include('TYPE_NO-CHANGES@125');
        });
    });
});

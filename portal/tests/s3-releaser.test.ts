const chai = require('chai'),
    sinonChai = require('sinon-chai'),
    {S3Releaser} = require('../lib/s3-releaser'),
    {
        getComponentMock,
        getWorkflowMock,
        getGraphMock
    } = require('./mocks');

chai.should();
chai.use(sinonChai);


describe('s3-releaser', () => {
    let workflowMock,
        graphMock,
        addStepSpy;

    beforeEach(() => {
        workflowMock = getWorkflowMock();
        graphMock = getGraphMock();

        addStepSpy = graphMock.addStep;
    });

    describe('не вызывает пересборку', () => {
        it('если нет компонентов', async () => {
            const releaser = new S3Releaser({
                components: []
            }, workflowMock);

            const steps = await releaser.getComponentsToRebuild();
            steps.should.be.empty;
        });

        it('если среди компонентов нет компонентов с s3 правилами', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            const steps = await releaser.getComponentsToRebuild();
            steps.should.be.empty;
        });

        it('если среди компонентов нет компонентов с s3 правилами + forceRebuild', async () => {
            const releaser = new S3Releaser({
                forceRebuild: true,
                components: [
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            const steps = await releaser.getComponentsToRebuild();
            steps.should.be.empty;
        });

        it('если у компонентов нет изменений', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            const steps = await releaser.getComponentsToRebuild();
            steps.should.be.empty;
        });
    });

    describe('вызывает пересборку компонента', () => {
        it('если есть s3 компонент с изменениями', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('have-changes', true, true),
                    getComponentMock('have-changes-2', true, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            const steps = await releaser.getComponentsToRebuild();
            steps.should.deep.equal(['have-changes', 'have-changes-2']);
        });

        it('если изменений нет, но есть forceRebuild', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                forceRebuild: true
            }, workflowMock);

            const steps = await releaser.getComponentsToRebuild();
            steps.should.deep.equal(['no-changes', 'no-changes-2']);
        });
    });


    describe('не добавляет шаги деплоя', () => {
        it('если нет компонентов', async () => {
            const releaser = new S3Releaser({
                components: []
            }, workflowMock);

            await releaser.fillGraph(new Set([]), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если среди компонентов нет компонентов с s3 правилами', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            await releaser.fillGraph(new Set(['foo', 'null', 'qwe']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если среди компонентов нет компонентов с s3 правилами + forceRebuild', async () => {
            const releaser = new S3Releaser({
                forceRebuild: true,
                components: [
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            await releaser.fillGraph(new Set(['foo', 'null', 'qwe']), graphMock);

            addStepSpy.should.not.been.called;
        });

        it('если у компонентов нет изменений', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            await releaser.fillGraph(new Set(['foo', 'null']), graphMock);

            addStepSpy.should.not.been.called;
        });
    });

    describe('добавляет шаги деплоя', () => {
        it('если есть s3 компонент с изменениями', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('have-changes', true, true),
                    getComponentMock('have-changes-2', true, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            await releaser.fillGraph(new Set(['have-changes', 'have-changes-2', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledTwice;

            const calls = addStepSpy.getCalls();

            [
                'have-changes',
                'have-changes-2'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name]);

                call.should.have.property('name')
                    .which.equals('s3-deploy-' + name);

                call.should.have.property('isDeploy')
                    .which.equals(true);

            });
        });

        it('если изменений нет, но есть forceRebuild', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ],
                forceRebuild: true
            }, workflowMock);

            await releaser.fillGraph(new Set(['no-changes', 'no-changes-2', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledTwice;

            const calls = addStepSpy.getCalls();

            [
                'no-changes',
                'no-changes-2'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name]);

                call.should.have.property('name')
                    .which.equals('s3-deploy-' + name);

                call.should.have.property('isDeploy')
                    .which.equals(true);

            });
        });

        it('если изменений нет, но компонент в списке', async () => {
            const releaser = new S3Releaser({
                components: [
                    getComponentMock('no-changes', true, true, false),
                    getComponentMock('no-changes-2', true, false, false),
                    getComponentMock('foo', false, true),
                    getComponentMock('null', false, false)
                ]
            }, workflowMock);

            await releaser.fillGraph(new Set(['no-changes', 'no-changes-2', 'null', 'qwe']), graphMock);

            addStepSpy.should.been.calledTwice;

            const calls = addStepSpy.getCalls();

            [
                'no-changes',
                'no-changes-2'
            ].forEach((name, i) => {
                const call = calls[i].firstArg;
                call.should.have.property('deps')
                    .which.deep.equal(['step-' + name]);

                call.should.have.property('name')
                    .which.equals('s3-deploy-' + name);

                call.should.have.property('isDeploy')
                    .which.equals(true);

            });
        });
    });
});

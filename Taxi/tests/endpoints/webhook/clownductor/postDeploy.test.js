const {cloneDeep, last, get} = require('lodash');
const request = require('supertest');

const app = require('../../../../server/app');
const db = require('../../../../server/db');
const TrackerService = require('../../../../server/service/tracker');
const mockData = require('../webhook.mock');

describe('Проверка вебхука clownductor', () => {
    beforeAll(async () => {
        await db.connect();
    });

    test('Должно отправиться сообщение о деплое', async () => {
        const response = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(mockData.deployMessageInfo);

        expect(response.statusCode).toBe(200);
    });

    test('Сообщение не должно отправиться из-за пустого changelog', async () => {
        const response = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send({
                ...mockData.deployMessageInfo,
                meta: {
                    ...mockData.deployMessageInfo.meta,
                    changelog: undefined,
                },
            });

        expect(response.statusCode).toBe(400);
    });

    test('Сообщения о деплое prod -> unst', async () => {
        const prodDeploy = cloneDeep(mockData.deployMessageInfo);
        const unstDeploy = cloneDeep(mockData.deployMessageInfo);

        prodDeploy.meta.environment = 'stable';
        prodDeploy.meta.docker_image += Date.now();
        prodDeploy.meta.changelog = mockData.postDeployTicket1;
        unstDeploy.meta.environment = 'unstable';
        unstDeploy.meta.docker_image += Date.now();
        unstDeploy.meta.changelog = mockData.postDeployTicket1;

        const {tickets: ticket1} = JSON.parse(mockData.postDeployTicket1);
        const commentsBefore = await TrackerService.getAllComments(ticket1[0]);

        const prodResp = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(prodDeploy);

        expect(prodResp.statusCode).toBe(200);
        const unstResp = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(unstDeploy);

        expect(unstResp.statusCode).toBe(200);
        const commentsAfter = await TrackerService.getAllComments(ticket1[0]);

        expect(commentsBefore.length).toEqual(commentsAfter.length);
    }, 10000);

    test('Сообщения о деплое unst -> prod', async () => {
        const prodDeploy = cloneDeep(mockData.deployMessageInfo);
        const unstDeploy = cloneDeep(mockData.deployMessageInfo);

        prodDeploy.meta.environment = 'stable';
        prodDeploy.meta.docker_image += Date.now();
        prodDeploy.meta.changelog = mockData.postDeployTicket2;
        unstDeploy.meta.environment = 'unstable';
        unstDeploy.meta.docker_image += Date.now();
        unstDeploy.meta.changelog = mockData.postDeployTicket2;

        const {tickets: ticket2} = JSON.parse(mockData.postDeployTicket2);
        const commentsBefore = await TrackerService.getAllComments(ticket2[0]);

        const unstResp = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(unstDeploy);

        expect(unstResp.statusCode).toBe(200);
        const prodResp = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(prodDeploy);

        expect(prodResp.statusCode).toBe(200);
        const commentsAfter = await TrackerService.getAllComments(ticket2[0]);

        expect(commentsBefore.length).toEqual(commentsAfter.length);
    }, 10000);

    test('Сообщения о деплое test -> other -> unst', async () => {
        const unstDeploy = cloneDeep(mockData.deployMessageInfo);

        unstDeploy.meta.environment = 'unstable';
        unstDeploy.meta.docker_image += Date.now();
        unstDeploy.meta.changelog = mockData.postDeployTicket3;

        const {tickets: ticket3} = JSON.parse(mockData.postDeployTicket3);
        const commentsBefore = await TrackerService.getAllComments(ticket3[0]);

        const unstResp = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(unstDeploy);

        expect(unstResp.statusCode).toBe(200);
        const commentsAfter = await TrackerService.getAllComments(ticket3[0]);

        expect(commentsBefore.length).toEqual(commentsAfter.length);
    }, 10000);

    test('Сообщения о деплое test -> unst -> other -> unst', async () => {
        const unstDeploy = cloneDeep(mockData.deployMessageInfo);

        unstDeploy.meta.environment = 'unstable';
        unstDeploy.meta.docker_image += Date.now();
        unstDeploy.meta.changelog = mockData.postDeployTicket4;

        const {ticket: ticket4} = JSON.parse(mockData.postDeployTicket4);
        const commentsBefore = await TrackerService.getAllComments(ticket4);

        const unstResp = await request(app)
            .post('/api/webhook/clownductor/deploy')
            .send(unstDeploy);

        expect(unstResp.statusCode).toBe(200);
        const commentsAfter = await TrackerService.getAllComments(ticket4);

        expect(commentsAfter.length - commentsBefore.length).toEqual(1);

        const lastCommentId = get(last(commentsAfter), 'longId');
        const removeResp = await TrackerService.removeComment(ticket4, lastCommentId);

        expect(removeResp.status).toBe(204);
    }, 10000);

    afterAll(async done => {
        await db.disconnect(done);
    });
});

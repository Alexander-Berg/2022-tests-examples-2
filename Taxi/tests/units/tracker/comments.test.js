const TrackerService = require('../../../server/service/tracker');

const mockData = require('./tracker.mock');

describe('Проверка методов работы с комментариями', () => {
    test('Комментарий должен отправиться в задачу и удалиться', async () => {
        const resp = await TrackerService.sendComment(...mockData.sendComment);
        const {longId} = await resp.json();

        expect(resp.status).toBe(201);

        const removeResp = await TrackerService.removeComment(mockData.testTicket, longId);

        expect(removeResp.status).toBe(204);
    });

    test('Комментарий должен измениться', async () => {
        const resp = await TrackerService.editComment(mockData.editComment);

        expect(resp.status).toBe(200);
    });

    test('Должен вернуться список комментариев из задачи', async () => {
        const resp = await TrackerService.getAllComments(mockData.testTicket);

        expect(resp.length).toBeGreaterThan(0);
    });

    test('На несуществующую задачу должен вернуться пустой массив', async () => {
        const resp = await TrackerService.getAllComments(mockData.wrongTestTicket);

        expect(resp.length).toBe(0);
    });
});

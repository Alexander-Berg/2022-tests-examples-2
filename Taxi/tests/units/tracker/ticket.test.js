const TrackerService = require('../../../server/service/tracker');

const mockData = require('./tracker.mock');

describe('Проверка методов работы с тикетами', () => {
    test('Должен создаться тикет', async () => {
        const resp = await TrackerService.createTicket(mockData.createTicket);

        expect(resp.status).toBe(201);
    });

    test('Тикет должен отредактироваться', async () => {
        const resp = await TrackerService.editTicket(...mockData.editTicket);

        expect(resp.status).toBe(200);
    });

    test('Должен найтись один тикет', async () => {
        const resp = await TrackerService.searchTicket(mockData.searchTask);

        expect(resp.status).toBe(200);
        const data = await resp.json();

        expect(data).toHaveLength(1);
    });

    test('Тикет должен корректно переходить из статуса в статус', async () => {
        const respTo = await TrackerService.transferToStatus(...mockData.transfer, 'start_progress');

        expect(respTo.length).toBe(0);
        const respBack = await TrackerService.transferToStatus(...mockData.transfer, 'stop_progress');

        expect(respBack.length).toBe(0);
    });

    test('Тикет не должен переходить по неправильным переходам', async () => {
        // wrong transition
        const wrongTrans = await TrackerService.transferToStatus(...mockData.transfer, 'provide_info');

        expect(wrongTrans.length).toBe(1);
        // unexisting transition
        const unexistingTrans = await TrackerService.transferToStatus(...mockData.transfer, 'provide_info12345');

        expect(unexistingTrans.length).toBe(1);
    });
});

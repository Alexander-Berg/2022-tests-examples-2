const {requestServiceYaml} = require('../../../server/utils/fmServices');

describe('Проверка utils функций', () => {
    test('YAML несуществующего сервиса не должен найтись', async () => {
        const fakeServiceResp = await requestServiceYaml('test-service123', {serviceWithPrefix: true});

        expect(fakeServiceResp).toBeUndefined();
    });
});

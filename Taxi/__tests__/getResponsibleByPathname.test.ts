const CONFIG_MOCK = {
    lang: 'ru',
    backendConfigs: {
        ADMIN_SECTIONS_SETTINGS_V2: {
            taxi: {
                sections: [
                    {responsibleId: 'foo', path: '/foo'},
                    {responsibleId: 'bar', path: '/bar'},
                    {responsibleId: 'baz', path: '/baz/'},
                    {responsibleId: 'baz', path: '/bar/baz'}
                ],
                responsibles: [
                    {id: 'foo', data: {managers: ['x']}},
                    {id: 'bar', data: {managers: ['y']}},
                    {id: 'baz', data: {managers: ['z']}}
                ]
            }
        }
    },
    appType: 'taxi'
};

describe('getResponsibleByPathname', () => {
    beforeAll(() => {
        jest.mock('_pkg/config', () => CONFIG_MOCK);
    });

    it('Находит нужный элемент в конфиге', async () => {
        const {getResponsibleByPathname} = await import('../utils');
        const result = getResponsibleByPathname('/foo');

        expect(result).toStrictEqual({
            managers: ['x']
        });
    });

    it('Обрабатывает trailing slash в pathname', async () => {
        const {getResponsibleByPathname} = await import('../utils');
        const result = getResponsibleByPathname('/bar/');

        expect(result).toStrictEqual({
            managers: ['y']
        });
    });

    it('Обрабатывает trailing slash в path конфига', async () => {
        const {getResponsibleByPathname} = await import('../utils');
        const result = getResponsibleByPathname('/baz');

        expect(result).toStrictEqual({
            managers: ['z']
        });
    });

    it('Ранжирует выдачу по самому полному совпадению', async () => {
        const {getResponsibleByPathname} = await import('../utils');
        const result = getResponsibleByPathname('/bar/baz');

        expect(result).toStrictEqual({
            managers: ['z']
        });
    });

    it('Исключает неполное вхождение', async () => {
        const {getResponsibleByPathname} = await import('../utils');
        const result = getResponsibleByPathname('/bar2');

        expect(result).toBeUndefined();
    });
});

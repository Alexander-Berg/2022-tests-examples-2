/* eslint-disable max-len */
import {mapClientToServer, mapServerToClient} from './role';

describe('RoleAPI', () => {
    describe('mapClientToServer', () => {
        test('лишние поля выкидываются', () => {
            const role = {
                deletable: true,
                putable: true,
                counters: {},
                headcount: 3,
            };
            const mapped = mapClientToServer(role);
            Object.keys(role).forEach(key => expect(mapped).not.toHaveProperty(key));
        });

        test('undefined лимит выставляет флаг no_specific_limit', () => {
            expect(
                mapClientToServer({services: {taxi: {limit: undefined, no_specific_limit: false}}})
                    .services.taxi,
            ).toMatchObject({
                limit: undefined,
                no_specific_limit: true,
            });
        });
    });

    describe('mapServerToClient', () => {
        test('Если приходит no_specific_limit - лимит undefined, а само свойство не пробрасывается', () => {
            expect(
                mapServerToClient({
                    services: {taxi: {no_specific_limit: true, limit: 10, orders: {limit: 0}}},
                }),
            ).toMatchObject({
                services: {
                    taxi: {
                        limit: undefined,
                    },
                },
            });
            expect(
                mapServerToClient({services: {taxi: {no_specific_limit: true, orders: {limit: 0}}}})
                    .services.taxi,
            ).not.toHaveProperty('no_specific_limit');
        });

        test('Если приходит пустой лимит или бесконечный лимит - он превратится в undefined', () => {
            expect(
                mapServerToClient({services: {taxi: {limit: null, orders: {limit: 0}}}}),
            ).toMatchObject({
                services: {
                    taxi: {
                        limit: undefined,
                    },
                },
            });
            expect(
                mapServerToClient({services: {taxi: {limit: Infinity, orders: {limit: 0}}}}),
            ).toMatchObject({
                services: {
                    taxi: {
                        limit: undefined,
                    },
                },
            });
        });

        test('Нулевой лимит нормально пропустится', () => {
            expect(
                mapServerToClient({services: {taxi: {limit: 0, orders: {limit: 0}}}}),
            ).toMatchObject({services: {taxi: {limit: 0}}});
        });
    });
});

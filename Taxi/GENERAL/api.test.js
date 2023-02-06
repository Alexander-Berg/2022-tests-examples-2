import {mapClientToServerOnProfileUpdate, mapClientToServerOnUpdate} from './api';

describe('ClientAPI', () => {
    const services = {taxi: {}};
    describe('mapClientToServerOnUpdate', () => {
        it('заменяет пустой email на пустую строку', () =>
            expect(mapClientToServerOnUpdate({services})).toMatchObject({email: ''}));
        it('заменяет несколько пробелов на пустую строку', () =>
            expect(mapClientToServerOnUpdate({services, email: '  '})).toMatchObject({
                email: '',
            }));
        it('отрезает пробелы с краёв', () =>
            expect(
                mapClientToServerOnUpdate({services, email: '  test@somewhere.com '}),
            ).toMatchObject({
                email: 'test@somewhere.com',
            }));
        it('обрезает пробелы с краёв комментария', () =>
            expect(mapClientToServerOnUpdate({services, comment: ' test '})).toMatchObject({
                comment: 'test',
            }));
    });
    describe('mapClientToServerOnProfileUpdate', () => {
        it('оставляет только поля email и comment', () => {
            expect(
                mapClientToServerOnProfileUpdate({
                    email: 'test@test.com',
                    comment: 'comment',
                    'some other': 'other',
                    services,
                }),
            ).toEqual({email: 'test@test.com', comment: 'comment'});
        });
    });
});

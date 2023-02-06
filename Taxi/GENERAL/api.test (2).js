import {mapServerGeoObjectToClient, mapServerToClient, search} from './api';

describe('GeosearchAPI', () => {
    describe('mapServerGeoObjectToClient', () => {
        it('убирает слово "город" в начале', () => {
            expect(
                mapServerGeoObjectToClient({
                    city: 'город нью-васюки',
                }),
            ).toMatchObject({city: 'нью-васюки'});
        });
        it('убирает слово "город" в конце', () => {
            expect(mapServerGeoObjectToClient({city: 'небольшой город'})).toMatchObject({
                city: 'небольшой',
            });
        });
        it('не падает при пустом названии', () => {
            expect(mapServerGeoObjectToClient({city: ''})).toMatchObject({
                city: '',
            });
            expect(mapServerGeoObjectToClient({city: undefined})).toMatchObject({city: ''});
            expect(mapServerGeoObjectToClient({city: null})).toMatchObject({
                city: '',
            });
        });
    });
    describe('mapServerToClient', () => {
        it('обрабатывает массив ответов', () => {
            expect(mapServerToClient({objects: [{city: 'город Москва'}]})).toMatchObject([
                {city: 'Москва'},
            ]);
            expect(mapServerToClient()).toBeUndefined();
        });
    });
    describe('get', () => {
        it('докидывает нужные параметры в body и делает трансформацию', () => {
            expect(search({s: 'москва'})).toMatchObject({
                method: 'POST',
                body: {
                    s: 'москва',
                },
            });
        });
    });
});

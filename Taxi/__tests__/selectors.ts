import {getTariffDescription} from '../selectors/tariffs';
import descriptions from './mocks/descriptions.json';

declare const global: any;

describe('tariffs', () => {
    describe('getTariffsDescription', () => {
        const RealDate = Date;
        // мокаем глобальный Date, чтобы предсказать результат
        const mockDate = (day: number, hours: number, minutes: number) => {
            global.Date = function() {
                return {
                    getDay: () => day,
                    getHours: () => hours,
                    getMinutes: () => minutes,
                    // эти две функции не важны
                    getTime: () => 0,
                    getTimezoneOffset: () => 0,
                };
            };
        };

        afterEach(() => {
            global.Date = RealDate;
        });

        const TEST_ZONE = 'testZone';
        const TEST_TARIFF = 'testTariff';
        const state = {
            app: {
                zone: TEST_ZONE,
            },
            orderDraft: {
                tariff: TEST_TARIFF,
            },
            zoneInfo: {
                tariffsDescription: {
                    [TEST_TARIFF]: descriptions,
                },
            },
        };

        it('должен вернуть первое описание тарифа, если нет расписания для текущего дня', () => {
            // 0 0 0 не существующий день, часы и минуты в объекте описании
            mockDate(0, 0, 0);
            const priceGroup = getTariffDescription(state as any);

            expect(priceGroup.name).toEqual(descriptions[0].priceGroup.name);
        });

        it('должен вернуть второе описание, если подошло время', () => {
            mockDate(1, 9, 0);
            const priceGroup = getTariffDescription({...state} as any);

            expect(priceGroup.name).toEqual(descriptions[1].priceGroup.name);
        });

        it('должен вернуть третье описание, если подошло время', () => {
            mockDate(3, 22, 0);
            const priceGroup = getTariffDescription({...state} as any);

            expect(priceGroup.name).toEqual(descriptions[2].priceGroup.name);
        });
    });
});

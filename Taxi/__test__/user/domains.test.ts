import uniq from 'lodash/uniq';

import {getAvailableDomains} from '../../user';
import {
    DOMAINS_EMPTY_RESTRICTIONS,
    DOMAINS_ONE_RESTRICTION,
    DOMAINS_SEVERAL_RESTRICTIONS,
} from '../mock/USER_DOMAINS';

describe('Обработка доменов для пользователя / Получать доступные домены по рестрикшенам', () => {
    describe('Нет пути /v1/skills/values', () => {
        test('Возвращается пустой массив', () => {
            const domains = getAvailableDomains(DOMAINS_EMPTY_RESTRICTIONS);

            expect(domains).toStrictEqual([]);
        });
    });

    describe('Есть один раз путь /v1/skills/values', () => {
        test('Возвращается массив из уникальных значений единственного init.set', () => {
            const domains = getAvailableDomains(DOMAINS_ONE_RESTRICTION);

            expect(domains).toStrictEqual(uniq(
                DOMAINS_ONE_RESTRICTION[1].predicate.init.set,
            ));
        });
    });

    describe('Есть несколько раз путь /v1/skills/values', () => {
        test('Возвращается массив из уникальных значений всех init.set у пути', () => {
            const domains = getAvailableDomains(DOMAINS_SEVERAL_RESTRICTIONS);

            expect(domains).toStrictEqual(uniq(
                [
                    ...DOMAINS_SEVERAL_RESTRICTIONS[1].predicate.init.set,
                    ...DOMAINS_SEVERAL_RESTRICTIONS[2].predicate.init.set,
                    ...DOMAINS_SEVERAL_RESTRICTIONS[4].predicate.init.set,
                ],
            ));
        });
    });
});

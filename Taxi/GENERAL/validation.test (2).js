import {RestrictionTypes, RoleUtil} from '@yandex-taxi/corp-staff';

import {identity} from 'lodash';
import {validate} from 'perfecto';

import {usersValidator} from './validation';

describe('usersValidator', () => {
    const v = object =>
        validate(usersValidator({t: identity, state: {config: {phones: {rules: []}}}}), {object});
    describe('all', () => {
        test('all.role_id - обязательное поле', async () => {
            expect(
                await v({hierarchy: {role_id: undefined}, services: {taxi: {cost_centers: {}}}}),
            ).toMatchObject([{path: ['hierarchy', 'role_id'], message: 'validation.required'}]);
        });
        describe('Роль custom - "Остальные"', () => {
            test('Ошибки валидации требований оказываюется в all', async () => {
                const errors = await v({
                    hierarchy: {role_id: RoleUtil.CUSTOM},
                    services: {
                        taxi: {
                            restrictions: [{days: {}, type: RestrictionTypes.WeeklyDate}],
                        },
                    },
                });
                expect(errors).toContainEqual({
                    path: ['services', 'taxi', 'restrictions', 0, 'days'],
                    message: 'validation.restrictions.days.required',
                });
                expect(errors).toContainEqual({
                    path: ['services', 'taxi', 'restrictions', 0, 'start_time'],
                    message: 'validation.required',
                });
            });
            test('С этой ролью проверяется лимит на всех', async () => {
                const errors = await v({
                    hierarchy: {role_id: RoleUtil.CUSTOM},
                    services: {taxi: {limit: 'test'}},
                    users: [],
                });
                expect(errors).toContainEqual({
                    path: ['services', 'taxi', 'limit'],
                    message: 'validation.number.positive.or.empty',
                });
            });
        });
        test('Для обычных ролей ошибки валидации ограничений выбрасываются', async () => {
            const errors = await v({
                hierarchy: {role_id: 'some'},
                services: {taxi: {restrictions: [{days: {}, type: RestrictionTypes.WeeklyDate}]}},
            });
            expect(errors).not.toContainEqual({
                path: ['services', 'taxi', 'restrictions', 0, 'days'],
                message: 'validation.restrictions.days.required',
            });
        });
    });
});

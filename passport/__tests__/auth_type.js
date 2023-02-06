import metrics from '../../metrics';

import * as extracted from '../auth_type.js';

jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

describe('Complete.AuthType', () => {
    describe('sendMetrics', () => {
        it('should call metrics.send and metrics.goal', () => {
            const obj = {
                props: {
                    prefix: 'prefix'
                }
            };

            extracted.sendMetrics.call(obj);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Выбрать другой аккаунт']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${obj.props.prefix}_form_change_account`);
        });
    });
});

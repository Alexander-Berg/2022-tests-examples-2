import {isArray, isObject} from 'lodash';

import {GeotargetTypes} from '../../types';
import {getEmptyStory} from '../../utils';
import {preUpdate} from '../matchers';

const wentThrough = (value: any, key: string, cb: (val: any, key: string) => void) => {
    if (isArray(value)) {
        value.forEach(item => wentThrough(item, null, cb));
    }

    if (isObject(value)) {
        Object.keys(value).forEach(key => wentThrough((value as Indexed)[key], key, cb));
    }

    cb(value, key);
};

describe('stories api matchers', () => {
    describe('preUpdate', () => {
        test('return new object', () => {
            const model = getEmptyStory();
            const data = preUpdate(model);
            expect(data).not.toBe(model);
        });

        test('no $view property', () => {
            const data = preUpdate(getEmptyStory());
            expect(data).not.toHaveProperty('$view');
        });

        test('no cid properties', () => {
            const data = preUpdate(getEmptyStory());
            let cids = 0;
            const cb = (_: any, key: string) => cids += key === 'cid' ? 1 : 0;

            wentThrough(data, null, cb);

            expect(cids).toBe(0);
        });

        test('no range if no inner values', () => {
            const data = preUpdate({
                ...getEmptyStory(),
                experiment: {
                    range: {
                        from: '',
                        to: ''
                    }
                }
            });

            expect(data.experiment).not.toHaveProperty('range');
        });

        test('no empty from in range', () => {
            const data = preUpdate({
                ...getEmptyStory(),
                experiment: {
                    range: {
                        from: '',
                        to: 0
                    }
                }
            });

            expect(data.experiment.range).not.toHaveProperty('from');
        });

        test('no empty to in range', () => {
            const data = preUpdate({
                ...getEmptyStory(),
                experiment: {
                    range: {
                        from: 0,
                        to: ''
                    }
                }
            });

            expect(data.experiment.range).not.toHaveProperty('to');
        });

        test('range converted to numbers', () => {
            const data = preUpdate({
                ...getEmptyStory(),
                experiment: {
                    range: {
                        from: '0',
                        to: '1'
                    }
                }
            });

            expect(data.experiment.range.from).toBe(0);
            expect(data.experiment.range.to).toBe(1);
        });

        test('keep only one targeting', () => {
            const data = preUpdate({
                ...getEmptyStory(),
                $view: {
                    targetType: GeotargetTypes.Zones
                },
                targeting: {
                    countries: ['111'],
                    zones: ['222']
                }
            });

            expect(data.targeting).not.toHaveProperty('countries');
        });
    });
});

import {push} from 'react-router-redux';
import {setEditMode} from '../../../../common/actions';

import * as extracted from '../social_block.js';

jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));

describe('Morda.SocialBlock', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                settings: {},
                dispatch: jest.fn()
            }
        };
    });
    describe('addProfiles', () => {
        it('should dispatch setEditMode and call preventDefault', () => {
            const event = {
                preventDefault: jest.fn()
            };

            extracted.addProfiles.call(obj, event);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('social');
        });
        it('should dispatch push and call preventDefault', () => {
            const event = {
                preventDefault: jest.fn()
            };

            obj.props.settings.isTouch = true;

            extracted.addProfiles.call(obj, event);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(extracted.link);
        });
    });

    describe('sortProfiles', () => {
        it('should return null', () => {
            expect(extracted.sortProfiles()).toBe(null);
            expect(extracted.sortProfiles([])).toBe(null);
        });
        it('should return sorted array', () => {
            const profiles = [
                {
                    someData: 'someData',
                    provider: {
                        code: 'code'
                    }
                },
                {
                    someData: 'someData',
                    provider: {
                        code: 'code'
                    }
                }
            ];

            expect(extracted.sortProfiles(profiles)).toEqual({
                code: [profiles[0], profiles[1]]
            });
        });
    });
});

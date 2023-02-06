import _ from 'lodash';

import createActions from '../createActions';

describe('utils:createEntityReducer:createActions', () => {
    test('should not create actions with the same type', () => {
        const actions = createActions({
            request: 'TEST',
            load: 'TEST',
            create: 'TEST',
            remove: 'TEST',
            update: 'TEST',
            find: 'TEST'
        });
        const generatedActionTypes = _.map(actions, action => action().type);

        expect((new Set(generatedActionTypes)).size).toEqual(Object.keys(actions).length);
    });

    test('should throw an error for uncofigured action creator call', () => {
        const unconfiguredActions = createActions({});

        _.forEach(unconfiguredActions, action => {
            expect(() => action()).toThrow(
                /Actions of kind "(request|load|create|remove|update|find)" weren't set up correctly/
            );
        });
    });
});

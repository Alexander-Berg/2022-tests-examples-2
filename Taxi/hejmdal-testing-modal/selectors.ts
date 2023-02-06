import {createSelector} from 'reselect';

import {getOperation, getStrictModel} from '_infrastructure/selectors';
import {isNotEmpty} from '_utils/strict/validators';

import {HEJMDAL_TESTING_MODEL, LOAD_TESTS_LIST} from './consts';

export const getModel = getStrictModel(HEJMDAL_TESTING_MODEL);

export const getIsRunAllAvailable = createSelector(
    getModel,
    model => isNotEmpty(model.enabled) || isNotEmpty(model.disabled)
);

export const getIsRunSelectedAvailable = createSelector(
    getModel,
    model => Object.values(model.enabled).some(Boolean) || Object.values(model.disabled).some(Boolean)
);

export const getIsEnabledMap = createSelector(getOperation(LOAD_TESTS_LIST), ({result}) => {
    const map: Record<string, boolean> = {};

    if (!result) {
        return map;
    }

    for (const item of [...result.enabled, ...result.disabled]) {
        map[item.id] = item.is_enabled;
    }

    return map;
});

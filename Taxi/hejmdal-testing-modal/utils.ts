import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';
import {toNumber} from '_utils/strict/parser';
import {isNotEmpty} from '_utils/strict/validators';

import {HEJMDAL_TESTING_MODEL} from './consts';
import {SelectedMap, TestCaseListItem, TestStatus} from './types';

export const path = modelPath(HEJMDAL_TESTING_MODEL);

export const createSelectedPath = (model: StrictModel<SelectedMap>) => modelPath(model);

export function createSelectedMap(arr: TestCaseListItem[]): SelectedMap {
    return arr.reduce<Record<number, boolean>>((result, current) => {
        result[current.id] = false;
        return result;
    }, {});
}

export function extractIdsFromSelectedMap(map: SelectedMap, onlySelected: boolean): number[] {
    return Object.entries(map).reduce<number[]>((result, [key, isSelected]) => {
        const id = toNumber(key);

        if (onlySelected && !isSelected) {
            return result;
        }

        if (isNotEmpty(id)) {
            result.push(id);
        }

        return result;
    }, []);
}

export function getStatus(passed?: boolean, ignored?: boolean, error?: boolean) {
    return passed ? TestStatus.Success : ignored ? TestStatus.Default : error ? TestStatus.Error : undefined;
}

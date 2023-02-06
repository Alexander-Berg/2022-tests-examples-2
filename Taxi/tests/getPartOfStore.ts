import set from 'lodash/set';

export function getStoreByPart<S>(path: string, part: S): GlobalStateType {
    const store = set<GlobalStateType>({}, path, part);

    return store;
};

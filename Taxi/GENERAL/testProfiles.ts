import {TestProfile} from './core/types';

export const enum TestProfileTypes {
    Local = 'local',
    Full = 'full'
}

export const local: TestProfile = {
    testCount: 1,
    retries: 1
};

export const full: TestProfile = {
    testCount: 20,
    retries: 3
};

export function getTestProfile(profileType: TestProfileTypes) {
    switch (profileType) {
        case TestProfileTypes.Full:
            return full;
        case TestProfileTypes.Local:
        default:
            return local;
    }
}

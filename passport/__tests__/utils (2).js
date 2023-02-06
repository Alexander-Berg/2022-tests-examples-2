import {RegType} from '@blocks/authv2/nativeMobileApi/constants';
import {getProcessName, getSteps} from '../utils';
import {
    ENTRY_REGISTER_ROUTE,
    ENTRY_RESTORE_ROUTE,
    ENTRY_RESTORE_NEOPHONISH_ROUTE,
    ENTRY_REGISTER_PROCESS,
    ENTRY_RESTORE_PROCESS,
    ENTRY_RESTORE_NEOPHONISH_PROCESS,
    ENTRY_REGISTER_NEOPHONISH_PROCESS,
    ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_PROCESS,
    ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_NEOPHONISH_PROCESS
} from '../processes';
import {
    REGISTER_NEOPHONISH_STEPS,
    REGISTER_NEOPHONISH_STEPS_WITHOUT_PERSONAL_DATA,
    COMMON_STEPS,
    COMMON_STEPS_WITHOUT_PERSONAL_DATA
} from '../steps';

describe('UserEntryFlow#utils', () => {
    it('should get undefined process', () => {
        expect(getProcessName({})).toBeUndefined();
    });

    [
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                }
            },
            ENTRY_REGISTER_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_RESTORE_ROUTE
                    }
                }
            },
            ENTRY_RESTORE_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_RESTORE_NEOPHONISH_ROUTE
                    }
                }
            },
            ENTRY_RESTORE_NEOPHONISH_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                signup: {
                    config: {
                        registerWithFullPersonalInfoOrigins: ['test']
                    }
                },
                common: {
                    origin: 'test'
                }
            },
            ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                signup: {
                    config: {
                        registerWithFullPersonalInfoOrigins: ['test']
                    }
                },
                customs: {
                    isNeoPhonishRegisterAvailable: true
                },
                common: {
                    origin: 'test'
                }
            },
            ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_NEOPHONISH_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                customs: {
                    isNeoPhonishRegisterAvailable: true
                },
                common: {
                    origin: 'test'
                }
            },
            ENTRY_REGISTER_NEOPHONISH_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                customs: {
                    isNeoPhonishRegisterAvailable: true
                },
                common: {
                    origin: 'test'
                },
                am: {
                    isAm: true,
                    regType: 'neophonish'
                }
            },
            ENTRY_REGISTER_NEOPHONISH_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                customs: {
                    isNeoPhonishRegisterAvailable: true
                },
                common: {
                    origin: 'test'
                },
                am: {
                    isAm: true,
                    regType: 'portal'
                }
            },
            ENTRY_REGISTER_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                customs: {
                    isNeoPhonishRegisterAvailable: false
                },
                common: {
                    origin: 'test'
                },
                am: {
                    isAm: true,
                    regType: 'portal'
                }
            },
            ENTRY_REGISTER_PROCESS
        ],
        [
            {
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                customs: {
                    isNeoPhonishRegisterAvailable: false
                },
                common: {
                    origin: 'test'
                },
                am: {
                    isAm: true,
                    regType: 'neophonish'
                }
            },
            ENTRY_REGISTER_NEOPHONISH_PROCESS
        ]
    ].forEach(([state, expectedProcess]) => {
        it(`should get ${expectedProcess} process`, () => {
            expect(getProcessName(state)).toEqual(expectedProcess);
        });
    });

    it('should get ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_NEOPHONISH_PROCESS when am.mode=turbo', () => {
        expect(
            getProcessName({
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                am: {
                    isAm: true,
                    mode: 'turbo',
                    regType: RegType.NEOPHONISH
                }
            })
        ).toEqual(ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_NEOPHONISH_PROCESS);
    });

    it('should get ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_PROCESS when am.mode=turbo', () => {
        expect(
            getProcessName({
                router: {
                    location: {
                        pathname: ENTRY_REGISTER_ROUTE
                    }
                },
                am: {
                    isAm: true,
                    mode: 'turbo',
                    regType: RegType.PORTAL
                }
            })
        ).toEqual(ENTRY_REGISTER_WITH_FULL_PERSONAL_INFO_PROCESS);
    });

    it.each([
        [ENTRY_REGISTER_NEOPHONISH_PROCESS, false, REGISTER_NEOPHONISH_STEPS],
        [ENTRY_REGISTER_NEOPHONISH_PROCESS, true, REGISTER_NEOPHONISH_STEPS_WITHOUT_PERSONAL_DATA],
        [ENTRY_RESTORE_NEOPHONISH_PROCESS, false, COMMON_STEPS],
        [ENTRY_RESTORE_NEOPHONISH_PROCESS, true, COMMON_STEPS_WITHOUT_PERSONAL_DATA]
    ])('should on getSteps(%s, %s) return %s', (process, useNewSuggestByPhone, expected) => {
        expect(getSteps(process, useNewSuggestByPhone)).toEqual(expected);
    });
});

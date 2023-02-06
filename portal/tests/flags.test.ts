/* eslint-disable @typescript-eslint/no-explicit-any */

import * as fs from 'fs';
import { mockReq } from '@lib/views/mockReq';
import { logError } from '@lib/log/logError';
import { checkFlag, getFlag, setFlagsDesc } from '../flags';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;
jest.mock('fs', () => ({
    readFileSync(path: fs.PathLike | number) {
        if (typeof path === 'string' && path.endsWith('/test.json')) {
            return JSON.stringify({
                test_flag: {
                    date: '26.03.2019',
                    description: 'HOME-0: Флаг для примера заполнения файла и тестов',
                    manager: '4eb0da',
                    expire: '01.01.2219'
                }
            });
        }
    },
    existsSync(path: fs.PathLike) {
        if (typeof path === 'string' && path.endsWith('/test.json')) {
            return true;
        }
    }
}));

describe('flags', function() {
    beforeEach(() => {
        setFlagsDesc('test.json');
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('get', function() {
        test('handles empty data', function() {
            expect(getFlag(mockReq(), 'test_flag')).toBeUndefined();

            expect(getFlag(mockReq({}, {
                ab_flags: null as any
            }), 'test_flag')).toBeUndefined();

            expect(getFlag(mockReq({}, {
                ab_flags: {} as any
            }), 'test_flag')).toBeUndefined();

            expect(getFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {}
                } as any
            }), 'test_flag')).toBeUndefined();
        });

        test('handles default value', function() {
            expect(getFlag(mockReq(), 'test_flag', 'red')).toEqual('red');

            expect(getFlag(mockReq({}, {
                ab_flags: null as any
            }), 'test_flag', 'red')).toEqual('red');

            expect(getFlag(mockReq({}, {
                ab_flags: {} as any
            }), 'test_flag', 'red')).toEqual('red');

            expect(getFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {}
                } as any
            }), 'test_flag', 'red')).toEqual('red');

            expect(getFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: 'blue'
                    }
                }
            }), 'test_flag', 'red')).toEqual('blue');
        });

        test('handles missing description', function() {
            mockedLogError.mockImplementation(() => {});

            expect(getFlag(mockReq(), 'missing_flag')).toBeUndefined();
            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });

        test('handles enabled flag', function() {
            expect(getFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: ''
                    }
                }
            }), 'test_flag')).toEqual('');

            expect(getFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: 'yellow'
                    }
                }
            }), 'test_flag')).toEqual('yellow');

            expect(getFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: 234
                    }
                } as any
            }), 'test_flag')).toEqual(234);
        });
    });

    describe('checkBool', function() {
        test('handles missing description', function() {
            mockedLogError.mockImplementation(() => {});

            expect(checkFlag(mockReq(), 'missing_flag')).toEqual(false);
            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });

        test('handles enabled flag', function() {
            expect(checkFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: ''
                    }
                }
            }), 'test_flag')).toEqual(false);

            expect(checkFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: 'no'
                    }
                }
            }), 'test_flag')).toEqual(false);

            expect(checkFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: 'yes'
                    }
                }
            }), 'test_flag')).toEqual(false);

            expect(checkFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: '1'
                    }
                }
            }), 'test_flag')).toEqual(true);

            expect(checkFlag(mockReq({}, {
                ab_flags: {
                    test_flag: {
                        value: 1
                    }
                } as any
            }), 'test_flag')).toEqual(true);
        });
    });
});

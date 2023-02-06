import {
    GET_TOKENS_BY_DEVICE,
    UPDATE_DEVICE_TOKEN_TAB,
    SHOW_DISABLING_TOKENS,
    SHOW_SAME_NAME_DEVICES,
    UPDATE_DISABLE_LIST,
    UPDATE_DEVICES_DISABLE_LIST
} from '../actions';
import reducer from '../reducers';

const state = {
    tokens: {
        deviceTokens: null,
        otherTokens: null,
        isYandexTokens: null
    },
    showDisablingList: false,
    disableDeviceId: '',
    deviceName: '',
    otherTokensToDelete: [],
    devicesToDelete: []
};

describe('Morda.Devices.reducers', () => {
    it('should set tokens', () => {
        const action = {
            type: GET_TOKENS_BY_DEVICE,
            list: [1, 2, 3]
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                tokens: action.list
            })
        );
    });
    it('should set disableDeviceId, showDisablingList and deviceName', () => {
        const action = {
            type: SHOW_DISABLING_TOKENS,
            info: {
                deviceId: 'value',
                deviceName: 'value',
                show: 'value'
            }
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                disableDeviceId: action.info.deviceId,
                showDisablingList: action.info.show,
                deviceName: action.info.deviceName
            })
        );
    });
    describe(SHOW_SAME_NAME_DEVICES, () => {
        it('should set deviceName', () => {
            const action = {
                type: SHOW_SAME_NAME_DEVICES,
                deviceName: 'value'
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    tokens: Object.assign({}, state.tokens, {
                        deviceTokens: []
                    }),
                    deviceName: action.deviceName
                })
            );
        });
        it('should set showDuble to 0 of sime deviceTokens', () => {
            const action = {
                type: SHOW_SAME_NAME_DEVICES,
                deviceName: 'value'
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    deviceTokens: [
                        {
                            deviceId: 'id'
                        },
                        {
                            deviceId: 'id2',
                            showDuble: 1
                        }
                    ]
                }
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    tokens: {
                        deviceTokens: [
                            {
                                deviceId: 'id'
                            },
                            {
                                deviceId: 'id2',
                                showDuble: 0
                            }
                        ]
                    },
                    deviceName: action.deviceName
                })
            );
        });
        it('should toggle showDouble of deviceTokens', () => {
            const action = {
                type: SHOW_SAME_NAME_DEVICES,
                idList: ['id', 'id2', 'id3']
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    deviceTokens: [
                        {
                            deviceId: 'id',
                            showDuble: 1
                        },
                        {
                            deviceId: 'id2',
                            showDuble: 0
                        }
                    ]
                }
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    tokens: {
                        deviceTokens: [
                            {
                                deviceId: 'id',
                                showDuble: 0
                            },
                            {
                                deviceId: 'id2',
                                showDuble: 1
                            }
                        ]
                    },
                    deviceName: ''
                })
            );
        });
        it('should set showDouble of deviceTokens to 0', () => {
            const action = {
                type: SHOW_SAME_NAME_DEVICES
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    deviceTokens: [
                        {
                            deviceId: 'id',
                            showDuble: 1
                        },
                        {
                            deviceId: 'id2',
                            showDuble: 1
                        }
                    ]
                }
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    tokens: {
                        deviceTokens: [
                            {
                                deviceId: 'id',
                                showDuble: 0
                            },
                            {
                                deviceId: 'id2',
                                showDuble: 0
                            }
                        ]
                    },
                    deviceName: ''
                })
            );
        });
    });
    describe(UPDATE_DISABLE_LIST, () => {
        it('should clear otherTokensToDelete', () => {
            const action = {
                type: UPDATE_DISABLE_LIST
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    otherTokensToDelete: []
                })
            );
        });
        it('should remove one item to otherTokensToDelete', () => {
            const action = {
                type: UPDATE_DISABLE_LIST,
                info: {
                    id: 'id'
                }
            };
            const copy = Object.assign({}, state, {
                otherTokensToDelete: ['id', 'id2']
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    otherTokensToDelete: ['id2']
                })
            );
        });
        it('should add one item to otherTokensToDelete', () => {
            const action = {
                type: UPDATE_DISABLE_LIST,
                info: {
                    state: 'checked',
                    id: 'id',
                    type: 'value'
                }
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    otherTokensToDelete: state.otherTokensToDelete.concat({id: action.info.id, type: action.info.type})
                })
            );
        });
    });
    it('should set devicesToDelete', () => {
        const action = {
            type: UPDATE_DEVICES_DISABLE_LIST,
            idList: [1, 2, 3]
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                devicesToDelete: action.idList
            })
        );
    });
    describe(UPDATE_DEVICE_TOKEN_TAB, () => {
        it('should return same state', () => {
            const action = {
                type: UPDATE_DEVICE_TOKEN_TAB
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    isYandexTokens: []
                }
            });

            expect(reducer(copy, action)).toEqual(copy);
        });
        it('should set tabOpened of isYandexTokens', () => {
            const action = {
                type: UPDATE_DEVICE_TOKEN_TAB
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    isYandexTokens: [
                        {
                            tabOpened: true
                        }
                    ]
                }
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    tokens: {
                        isYandexTokens: [
                            {
                                tabOpened: false
                            }
                        ]
                    }
                })
            );
        });
        it('should toggle tabOpened one of deviceTokens', () => {
            const action = {
                type: UPDATE_DEVICE_TOKEN_TAB,
                tokenType: 'deviceTokens',
                id: 1
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    deviceTokens: [
                        {
                            tokens: [
                                {
                                    tokenId: 1,
                                    tabOpened: true
                                }
                            ]
                        },
                        {
                            tokens: [
                                {
                                    tokenId: 2,
                                    tabOpened: true
                                }
                            ]
                        }
                    ]
                }
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    tokens: {
                        deviceTokens: [
                            {
                                tokens: [
                                    {
                                        tokenId: 1,
                                        tabOpened: false
                                    }
                                ]
                            },
                            {
                                tokens: [
                                    {
                                        tokenId: 2,
                                        tabOpened: true
                                    }
                                ]
                            }
                        ]
                    }
                })
            );
        });
        it('should toggle tabOpened one of otherTokens', () => {
            const action = {
                type: UPDATE_DEVICE_TOKEN_TAB,
                tokenType: 'otherTokens',
                id: 1
            };
            const copy = Object.assign({}, state, {
                tokens: {
                    otherTokens: [
                        {
                            tokenId: 1,
                            tabOpened: true
                        },
                        {
                            tokenId: 2,
                            tabOpened: true
                        }
                    ]
                }
            });

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    tokens: {
                        otherTokens: [
                            {
                                tokenId: 1,
                                tabOpened: false
                            },
                            {
                                tokenId: 2,
                                tabOpened: true
                            }
                        ]
                    }
                })
            );
        });
    });
    it('should return same state', () => {
        expect(reducer(undefined, {})).toEqual(state);
    });
});

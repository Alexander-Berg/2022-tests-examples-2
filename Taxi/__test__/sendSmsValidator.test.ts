import {expectSaga} from 'redux-saga-test-plan';

import {MODELS} from '../../consts';
import {sendSmsValidator} from '../validators';

const getState = (cb: () => any) => {
    return {
        [MODELS.SEND_SMS]: cb()
    };
};

const makeValidationResult = (isValid: boolean, validity: Indexed) => {
    return {
        isValid,
        validity,
        errors: {}
    };
};

describe('sendSmsValidator', () => {
    describe('просто текст', () => {
        test('валидная модель', () => {
            return expectSaga(sendSmsValidator)
                .withState(
                    getState(() => {
                        return {
                            text: {
                                useTanker: false,
                                text: 'str',
                                tanker: {
                                    key: '',
                                    keyset: '',
                                    params: []
                                }
                            },
                            phone: '123',
                            recipients_type: 'str'
                        };
                    })
                )
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toEqual(
                        makeValidationResult(true, {
                            'phone': false,
                            'recipients_type': false,
                            'text.text': false
                        })
                    );
                });
        });

        test('невалидная модель', () => {
            return expectSaga(sendSmsValidator)
                .withState(
                    getState(() => {
                        return {
                            text: {
                                useTanker: false,
                                text: '',
                                tanker: {
                                    key: '',
                                    keyset: '',
                                    params: []
                                }
                            },
                            phone: '',
                            recipients_type: ''
                        };
                    })
                )
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toEqual(
                        makeValidationResult(false, {
                            'phone': true,
                            'recipients_type': true,
                            'text.text': true
                        })
                    );
                });
        });
    });

    describe('танкер', () => {
        test('валидная модель', () => {
            return expectSaga(sendSmsValidator)
                .withState(
                    getState(() => {
                        return {
                            text: {
                                useTanker: true,
                                text: '',
                                tanker: {
                                    key: 'str',
                                    keyset: 'str',
                                    params: [
                                        {
                                            key: 'str',
                                            value: 'str'
                                        }
                                    ]
                                }
                            },
                            phone: '123',
                            recipients_type: 'str'
                        };
                    })
                )
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toEqual(
                        makeValidationResult(true, {
                            'phone': false,
                            'recipients_type': false,
                            'text.tanker.key': false,
                            'text.tanker.keyset': false,
                            'text.tanker.params.0.key': false,
                            'text.tanker.params.0.value': false
                        })
                    );
                });
        });

        test('невалидная модель', () => {
            return expectSaga(sendSmsValidator)
                .withState(
                    getState(() => {
                        return {
                            text: {
                                useTanker: true,
                                text: '',
                                tanker: {
                                    key: '',
                                    keyset: '',
                                    params: [
                                        {
                                            key: '',
                                            value: ''
                                        }
                                    ]
                                }
                            },
                            phone: '',
                            recipients_type: ''
                        };
                    })
                )
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toEqual(
                        makeValidationResult(false, {
                            'phone': true,
                            'recipients_type': true,
                            'text.tanker.key': true,
                            'text.tanker.keyset': true,
                            'text.tanker.params.0.key': true,
                            'text.tanker.params.0.value': true
                        })
                    );
                });
        });
    });
});

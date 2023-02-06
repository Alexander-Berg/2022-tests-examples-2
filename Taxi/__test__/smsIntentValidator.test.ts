import {cloneDeep} from 'lodash';
import {expectSaga} from 'redux-saga-test-plan';

import i18n from '_utils/localization/i18n';

import {MODELS} from '../../consts';
import {smsIntentValidator} from '../validators';

const EMPTY_MODEL = {
    intent: 'str',
    settings: {
        info: {
            description: 'str',
            recipients_type: ['user'],
            business_group: 'str',
            cost_center: 'str',
            meta_type: 'str',
            responsible: ['str'],
            is_marketing: false
        },
        technical: {
            use_fallback_queue: false,
            use_whitelist: false,
            provider: {
                name: 'yasms',
                sender: '',
                is_sender_changeable: false
            }
        },
        texts: {
            is_automatic: false
        }
    }
};

const EMPTY_MODEL_VALIDITY_RESULT = {
    'intent': false,
    'settings.info.description': false,
    'settings.info.recipients_type': false,
    'settings.info.business_group': false,
    'settings.info.cost_center': false,
    'settings.info.meta_type': false,
    'settings.info.is_marketing': false,
    'settings.technical.mask_text': false,
    'settings.technical.message_ttl': false,
    'settings.technical.use_fallback_queue': false,
    'settings.technical.pass_user_agent': false,
    'settings.technical.ignore_errors': false,
    'settings.technical.use_whitelist': false,
    'settings.technical.notification_instead_sms': false,
    'settings.technical.request_idempotency': false,
    'settings.technical.provider.name': false,
    'settings.technical.provider.sender': false,
    'settings.technical.provider.is_sender_changeable': false,
    'settings.technical.provider.settings': false,
    'settings.texts.is_automatic': false,
    'settings.texts.allowed_translations': false
};

const getState = (cb: (model: any) => any) => {
    return {
        [MODELS.INTENT]: cb(cloneDeep(EMPTY_MODEL))
    };
};

const makeValidationResult = (isValid: boolean, validity: Indexed, errors: Indexed = {}) => {
    return {
        isValid,
        validity,
        errors
    };
};

describe('smsIntentValidator', () => {
    test('невалидная модель', () => {
        return expectSaga(smsIntentValidator)
            .withState(
                getState(model => {
                    model.intent = '';

                    model.settings.info = {
                        description: '',
                        recipients_type: [],
                        business_group: '',
                        cost_center: '',
                        meta_type: '',
                        responsible: [],
                        is_marketing: 'false'
                    };

                    model.settings.technical = {
                        mask_text: 'str',
                        message_ttl: 'str',
                        use_fallback_queue: 'str',
                        pass_user_agent: 'str',
                        ignore_errors: ['str'],
                        use_whitelist: 'str',
                        provider: {
                            name: 'str',
                            sender: 999,
                            is_sender_changeable: 'str'
                        },
                        request_idempotency: {
                            enabled: 'str',
                            token_ttl: 'str'
                        },
                        notification_instead_sms: {
                            enabled: 'str',
                            payload_template_name: 999,
                            send_only_if_has_notification: 'str',
                            phone_type: 999,
                            applications: [''],
                            acknowledge_ttl: -999,
                            delivery_ttl: '999'
                        }
                    };

                    model.settings.texts = {
                        is_automatic: 'false',
                        allowed_translations: [
                            {
                                keyset: '',
                                key: ''
                            }
                        ]
                    };

                    return model;
                })
            )
            .run()
            .then(({returnValue}) => {
                expect(returnValue).toEqual(
                    makeValidationResult(
                        false,
                        {
                            'intent': true,
                            'settings.info.is_marketing': true,
                            'settings.info.business_group': true,
                            'settings.info.cost_center': true,
                            'settings.info.description': true,
                            'settings.info.meta_type': true,
                            'settings.info.recipients_type': true,
                            'settings.technical.mask_text': true,
                            'settings.technical.message_ttl': true,
                            'settings.technical.use_fallback_queue': true,
                            'settings.technical.pass_user_agent': true,
                            'settings.technical.ignore_errors': true,
                            'settings.technical.use_whitelist': true,
                            'settings.technical.notification_instead_sms': undefined,
                            'settings.technical.notification_instead_sms.enabled': true,
                            'settings.technical.notification_instead_sms.payload_template_name': true,
                            'settings.technical.notification_instead_sms.send_only_if_has_notification': true,
                            'settings.technical.notification_instead_sms.phone_type': true,
                            'settings.technical.notification_instead_sms.applications.0': true,
                            'settings.technical.notification_instead_sms.acknowledge_ttl': true,
                            'settings.technical.notification_instead_sms.delivery_ttl': true,
                            'settings.technical.provider.name': true,
                            'settings.technical.provider.sender': true,
                            'settings.technical.provider.is_sender_changeable': true,
                            'settings.technical.provider.settings': true,
                            'settings.technical.request_idempotency': undefined,
                            'settings.technical.request_idempotency.enabled': true,
                            'settings.technical.request_idempotency.token_ttl': true,
                            'settings.texts.is_automatic': true,
                            'settings.texts.allowed_translations': undefined,
                            'settings.texts.allowed_translations.0.key': true,
                            'settings.texts.allowed_translations.0.keyset': true
                        },
                        {
                            'settings.info.responsible': i18n.print('sms-intents.responsible_error'),
                            'settings.info.responsible_groups': i18n.print('sms-intents.responsible_error')
                        }
                    )
                );
            });
    });

    test('валидная модель', () => {
        return expectSaga(smsIntentValidator)
            .withState(
                getState(model => {
                    model.settings.technical = {
                        mask_text: false,
                        message_ttl: 0,
                        use_fallback_queue: false,
                        pass_user_agent: true,
                        ignore_errors: ['limit_exceeded'],
                        use_whitelist: false,
                        provider: {
                            name: 'infobip',
                            sender: 'str',
                            is_sender_changeable: false,
                            settings: {
                                account: 'str',
                                default_alpha_name: 'str',
                                ttl: 100
                            }
                        },
                        request_idempotency: {
                            enabled: true,
                            token_ttl: 1000
                        },
                        notification_instead_sms: {
                            enabled: true,
                            payload_template_name: '',
                            send_only_if_has_notification: false,
                            phone_type: 'str',
                            applications: ['test'],
                            acknowledge_ttl: 100,
                            delivery_ttl: 100
                        }
                    };

                    model.settings.texts = {
                        is_automatic: true,
                        allowed_translations: [
                            {
                                keyset: 'str',
                                key: 'str'
                            }
                        ]
                    };

                    return model;
                })
            )
            .run()
            .then(({returnValue}) => {
                expect(returnValue).toEqual(
                    makeValidationResult(true, {
                        ...EMPTY_MODEL_VALIDITY_RESULT,
                        'settings.technical.notification_instead_sms': undefined,
                        'settings.technical.notification_instead_sms.applications.0': false,
                        'settings.technical.notification_instead_sms.acknowledge_ttl': false,
                        'settings.technical.notification_instead_sms.delivery_ttl': false,
                        'settings.technical.notification_instead_sms.enabled': false,
                        'settings.technical.notification_instead_sms.payload_template_name': false,
                        'settings.technical.notification_instead_sms.phone_type': false,
                        'settings.technical.notification_instead_sms.send_only_if_has_notification': false,
                        'settings.technical.provider.settings': undefined,
                        'settings.technical.provider.settings.account': false,
                        'settings.technical.provider.settings.default_alpha_name': false,
                        'settings.technical.provider.settings.ttl': false,
                        'settings.technical.request_idempotency': undefined,
                        'settings.technical.request_idempotency.enabled': false,
                        'settings.technical.request_idempotency.token_ttl': false,
                        'settings.texts.allowed_translations': undefined,
                        'settings.texts.allowed_translations.0.key': false,
                        'settings.texts.allowed_translations.0.keyset': false
                    })
                );
            });
    });

    describe('валидация поля settings.technical.provider', () => {
        test('провайдер yasms', () => {
            return expectSaga(smsIntentValidator)
                .withState(
                    getState(model => {
                        model.settings.technical.provider.name = 'yasms';
                        model.settings.technical.provider.settings = {
                            route: 'str'
                        };

                        return model;
                    })
                )
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toEqual(
                        makeValidationResult(false, {
                            ...EMPTY_MODEL_VALIDITY_RESULT,
                            'settings.technical.provider.settings': undefined,
                            'settings.technical.provider.settings.route': false,
                            'settings.technical.provider.settings.sender': true
                        })
                    );
                });
        });

        test('провайдер infobip', () => {
            return expectSaga(smsIntentValidator)
                .withState(
                    getState(model => {
                        model.settings.technical.provider.name = 'infobip';
                        model.settings.technical.provider.settings = {
                            account: 'str',
                            default_alpha_name: 'str'
                        };

                        return model;
                    })
                )
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toEqual(
                        makeValidationResult(true, {
                            ...EMPTY_MODEL_VALIDITY_RESULT,
                            'settings.technical.provider.settings': undefined,
                            'settings.technical.provider.settings.account': false,
                            'settings.technical.provider.settings.default_alpha_name': false,
                            'settings.technical.provider.settings.ttl': false
                        })
                    );
                });
        });
    });
});

import findFieldsWithErrors from '../methods/findFieldsWithErrors';
import {setFieldErrorActive} from '@blocks/actions/form';
import mockData from './__mocks__/data';

jest.mock('./basicRegistrationMethods', () => ({
    prepareFormData: jest.fn()
}));
jest.mock('@blocks/actions/form', () => ({
    setFieldErrorActive: jest.fn()
}));

describe('findFieldsWithErrors', () => {
    it('should do nothing if there is an active error in store', () => {
        const getState = () => ({
            settings: {
                language: 'ru',
                uatraits: {
                    isMobile: false,
                    isTouch: false
                }
            },
            common: {
                csrf: '12345',
                track_id: '1234',
                from: 'mail'
            },
            form: {
                values: {
                    firstname: 'test',
                    lastname: 'example',
                    email: 'test@example.com',
                    login: '',
                    password: ''
                },
                states: {
                    firstname: 'not_valid',
                    lastname: 'not_valid',
                    email: 'valid',
                    phone: 'valid'
                },
                errors: {
                    active: true,
                    firstname: {
                        code: 'missingvalue',
                        text: 'Пожалуйста, укажите имя'
                    },
                    lastname: {
                        code: '',
                        text: ''
                    },
                    phone: {
                        code: '',
                        text: ''
                    }
                }
            }
        });
        const result = findFieldsWithErrors()(mockData.props.dispatch, getState);

        expect(result).toBeUndefined();
    });
    it('should set not_valid status for invalid field', () => {
        const getState = () => ({
            settings: {
                language: 'ru',
                uatraits: {
                    isMobile: false,
                    isTouch: false
                }
            },
            common: {
                csrf: '12345',
                track_id: '1234',
                from: 'mail'
            },
            form: {
                values: {
                    firstname: 'test',
                    lastname: 'example',
                    email: 'test@example.com',
                    login: '',
                    password: ''
                },
                states: {
                    firstname: 'not_valid',
                    lastname: 'valid',
                    email: 'valid',
                    phone: 'valid'
                },
                errors: {
                    active: false,
                    firstname: {
                        code: 'missingvalue',
                        text: 'Пожалуйста, укажите имя'
                    },
                    lastname: {
                        code: '',
                        text: ''
                    },
                    phone: {
                        code: '',
                        text: ''
                    }
                },
                validation: {
                    method: 'phone',
                    humanConfirmationDone: false
                }
            }
        });

        findFieldsWithErrors()(mockData.props.dispatch, getState);
        expect(setFieldErrorActive).toBeCalled();
        expect(setFieldErrorActive).toBeCalledWith('firstname');
    });
});

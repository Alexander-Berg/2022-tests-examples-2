import checkIfInvalid from '../methods/checkIfInvalid';
import {updateErrors, setFieldErrorActive} from '@blocks/actions/form';

jest.mock('@blocks/actions/form', () => ({
    setFieldErrorActive: jest.fn(),
    updateErrors: jest.fn()
}));

const props = {
    dispatch: jest.fn()
};

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

describe('checkIfInvalid', () => {
    it('should dispatch setFieldErrorActive if field status invalid', () => {
        checkIfInvalid('firstname')(props.dispatch, getState);
        expect(setFieldErrorActive).toBeCalled();
    });
    it('should dispatch setFieldErrorActive if field status invalid', () => {
        checkIfInvalid('firstname')(props.dispatch, getState);
        expect(setFieldErrorActive).toBeCalled();
    });
    it('should dispatch updateErrors if field status invalid and !hasErrorText', () => {
        checkIfInvalid('lastname')(props.dispatch, getState);
        expect(updateErrors).toBeCalled();
    });
    it('should return undefined if field status valid', () => {
        const result = checkIfInvalid('phone')(props.dispatch, getState);

        expect(result).toBeUndefined();
    });
});

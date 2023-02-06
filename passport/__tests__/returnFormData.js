import returnFormData from '../methods/returnFormData';

const getStateWithPhone = () => ({
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
            lastname: 'testov',
            login: 'test123',
            password: 'simple',
            password_confirm: 'simple',
            hint_question_id: '',
            hint_question: '',
            hint_question_custom: '',
            hint_answer: '',
            captcha: '',
            phone: '+79091234567',
            phoneCode: '2132'
        },
        validation: {
            method: 'phone',
            humanConfirmationDone: true
        }
    }
});
const getStateWithCaptcha = () => ({
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
            lastname: 'testov',
            login: 'test123',
            password: 'simple',
            password_confirm: 'simple',
            hint_question_id: '99',
            hint_question: '',
            hint_question_custom: 'Test question',
            hint_answer: 'my test answer',
            captcha: 'qwerty',
            phone: '',
            phoneCode: ''
        },
        validation: {
            method: 'captcha',
            humanConfirmationDone: true
        }
    }
});
const dispatch = jest.fn();

describe('returnFormData', () => {
    it('should return object with form data', () => {
        const testFormData = {
            firstname: 'test',
            lastname: 'testov',
            login: 'test123',
            password: 'simple',
            password_confirm: 'simple',
            hint_question_id: '',
            hint_question: '',
            hint_question_custom: '',
            hint_answer: '',
            captcha: '',
            phone: '+79091234567',
            phoneCode: '2132',
            'human-confirmation': 'phone'
        };

        expect(returnFormData()(dispatch, getStateWithPhone)).toEqual(testFormData);
    });
    it('should have filled hint_question if method = captcha', () => {
        expect(returnFormData(true)(dispatch, getStateWithCaptcha)).toHaveProperty('hint_question', 'Test question');
    });
});

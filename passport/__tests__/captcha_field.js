import {handleCaptchaAnswerChange} from '../captcha_field.js';
import {changeCaptchaAnswer} from '../../actions';

jest.mock('../../actions', () => ({
    changeCaptchaAnswer: jest.fn()
}));

describe('Component: CaptchaField', () => {
    it('should dispatch change captcha answer with value', () => {
        const captchaAnswer = 'answer';
        const props = {
            dispatch: jest.fn()
        };

        handleCaptchaAnswerChange.call({props}, {target: {value: captchaAnswer}});

        expect(props.dispatch).toBeCalled();
        expect(changeCaptchaAnswer).toBeCalledWith(captchaAnswer);
    });
});

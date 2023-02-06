import * as extracted from '../create_app_password.js';
import {showRegPopup, setEditMode} from '../../../../../common/actions';

jest.mock('../../../../../common/actions', () => ({
    setEditMode: jest.fn(),
    showRegPopup: jest.fn()
}));

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));

describe('Morda.AuthBlock.CreateAppPassword', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                dispatch: jest.fn(),
                settings: {}
            }
        };
    });
    it('should dispatch showRegPopup', () => {
        obj.props.isSocialchik = true;

        extracted.showCreationPopup.call(obj);
        expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
        expect(showRegPopup).toHaveBeenCalledTimes(1);
        expect(showRegPopup).toHaveBeenCalledWith(true);
    });
    it('should dispatch setEditMode', () => {
        extracted.showCreationPopup.call(obj);
        expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
        expect(setEditMode).toHaveBeenCalledTimes(1);
        expect(setEditMode).toHaveBeenCalledWith('apppwd-create');
    });
});

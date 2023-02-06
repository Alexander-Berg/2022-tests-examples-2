import mapStateToProps from '../mapStateToProps';
import formatAccountListUrl from '../../../../utils/formatAccountListUrl';

jest.mock('../../../../utils/formatAccountListUrl');

describe('Components: SuggestedAccountListItem.mapStateToProps', () => {
    beforeAll(() => {
        formatAccountListUrl.mockImplementation((params) => params);
    });

    it('should return valid props', () => {
        const state = {
            settings: {
                avatar: 'avatarSettings',
                ua: {
                    isTouch: true
                }
            },
            common: {
                embeddedauth_url: 'embeddedAuthUrl',
                retpath: 'retpath',
                yu: 'yu'
            }
        };

        const ownProps = {
            account: {
                uid: 'uid'
            }
        };

        const result = mapStateToProps(state, ownProps);

        expect(result).toEqual({
            avatarSettings: 'avatarSettings',
            fallbackUrl: {
                action: 'switchTo',
                embeddedAuthUrl: 'embeddedAuthUrl',
                retpath: 'retpath',
                yu: 'yu',
                uid: 'uid'
            }
        });
        expect(formatAccountListUrl).toBeCalled();
        expect(formatAccountListUrl.mock.calls.length).toBe(1);
    });
});

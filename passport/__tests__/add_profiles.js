import broker from '../../../../broker';

import * as extracted from '../add_profiles.js';

jest.mock('../../../../broker', () => ({
    start: jest.fn()
}));

describe('SocialInfo.AddProfiles', () => {
    it('should return className', () => {
        const code = 'code';

        expect(extracted.getClassName(code)).toBe(`social-icon social-icon_${code} s-add-profiles__available-profile`);
    });
    it('should start broker', () => {
        const provider = 'provider';

        extracted.addSocialProfile(provider);
        expect(broker.start).toHaveBeenCalledTimes(1);
        expect(broker.start).toHaveBeenCalledWith({
            provider,
            require_auth: 1
        });
    });
});

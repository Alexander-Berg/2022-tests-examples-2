import {defineRegistrationFunction} from '@blocks/registration/methods/defineRegistrationFunction';

describe('defineRegistrationFunction', () => {
    it('should return registration function', () => {
        const result = defineRegistrationFunction('REGISTRATION_PDD_MOBILE_GOAL_PREFIX');

        expect(typeof result === 'function').toBeTruthy();
    });
});

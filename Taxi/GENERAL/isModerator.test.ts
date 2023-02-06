import { isModerator } from './isModerator';

describe('isModerator', () => {
  it('returns `true` if user is moderator', () => {
    expect(isModerator({ userId: 0, userType: 'MODERATOR' })).toBe(true);
  });

  it('returns `false` is user is not moderator', () => {
    expect(isModerator({ userId: 0, userType: 'USER' }));
  });
});

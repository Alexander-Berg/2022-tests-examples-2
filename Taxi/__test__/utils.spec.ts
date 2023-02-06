import {isConventionalFormat} from '../utils';

test('isConventionalFormat', () => {
    expect(isConventionalFormat(' TAXIFRONTINFRA-877: Разработать (#4146) ')).toBe(false);
    expect(isConventionalFormat('feat: [TEFADMIN-877] - Разработать (#4146)')).toBe(true);
    expect(isConventionalFormat('fix(services): [TEFADMIN-877]: Разработать (#4146)')).toBe(true);
    expect(isConventionalFormat('  chore(11):TEFADMIN-877 Разработать (#4146)')).toBe(false);
    expect(isConventionalFormat('fix(11): [TEFADMIN-877] Разработать (#4146)')).toBe(true);
    expect(isConventionalFormat('fix(11): TEFADMIN-877: Разработать (#4146)')).toBe(true);
});

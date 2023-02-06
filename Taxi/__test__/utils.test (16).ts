import {createBuildCommand, findTicket, getAllTickets, parseChangelog} from '../utils';

test('createBuildCommand', () => {
    expect(
        createBuildCommand('xxx', 'Dockerfile', {
            a: 'a',
            b: 'b'
        })
    ).toBe('docker build --no-cache --pull --build-arg a="a" --build-arg b="b" -q -f Dockerfile -t "xxx" .');
});

test('findTicket', () => {
    expect(findTicket(' TAXIFRONTINFRA-877: Разработать (#4146) ')).toBe('TAXIFRONTINFRA-877');
    expect(findTicket('CORPDEV-877 Разработать (#4146)')).toBe('CORPDEV-877');
    expect(findTicket('[TEFADMIN-877]: Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('[TEFADMIN-877] - Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('feat: [TEFADMIN-877] - Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('fix(services): [TEFADMIN-877]: Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('  chore(11):TEFADMIN-877 Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('fix(11): [TEFADMIN-877] Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('fix(11): TEFADMIN-877: Разработать (#4146)')).toBe('TEFADMIN-877');
    expect(findTicket('*   feat: [TEFADMIN-877] - Разработать (#4146)')).toBe('TEFADMIN-877');
});

test('parseChangelog', async () => {
    expect(await parseChangelog(`${__dirname}/CHANGELOG.md`, '0.163.0', '0.159.0')).toEqual([
        'TEFADMIN-200',
        'TEFADMIN-153'
    ]);
});

jest.mock('../../common/utils', () => ({
    getStableSHA: () => Promise.resolve('b2d1834b8aab62d3bf451387c67f5cc783d993e5')
}));

jest.mock('../../../common/vcs/arc', () => ({
    getLog: (...args: any[]) =>
        Promise.resolve([
            {
                commit: 'fd11c6c75aafeaceaa6769053b6fbe2ae104a405',
                author: 'ktnglazachev',
                date: '2022-03-30T18:55:54+03:00',
                message: '66 hotfix\n\nQUEUE-111: 111\n\nQUEUE-222: 222\n\nREVIEW: 2423127'
            },
            {
                commit: 'b2d1834b8aab62d3bf451387c67f5cc783d993e5',
                author: 'ktnglazachev',
                date: '2022-03-30T13:03:12+03:00',
                message: 'feat: QUEUE-333: 333'
            }
        ])
}));

test('getAllTickets', async () => {
    const tickets = await getAllTickets('');
    expect(tickets).toEqual(['QUEUE-111', 'QUEUE-222', 'QUEUE-333']);
});

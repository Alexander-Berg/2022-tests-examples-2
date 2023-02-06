import * as config from '../types.config.json';

describe('types.config', () => {
    test('default repositories and branches', () => {
        const actual = config.repositories.reduce((acc, repo) => {
            if (repo.vcs === 'arc') {
                acc[repo.name] = {
                    path: repo.path,
                    branch: repo.branch,
                };
            } else {
                acc[repo.name] = {
                    url: repo.url,
                    branch: repo.branch,
                };
            }
            return acc;
        }, {} as Indexed);
        const expected = {
            'backend-py3': {
                path: 'taxi/backend-py3',
                branch: 'trunk',
            },
            'backend-cpp': {
                url: 'https://github.yandex-team.ru/taxi/backend-cpp',
                branch: 'develop',
            },
            'uservices': {
                path: 'taxi/uservices',
                branch: 'trunk',
            },
            'backend': {
                url: 'https://github.yandex-team.ru/taxi/backend',
                branch: 'develop',
            },
        };
        expect(actual).toEqual(expected);
    });
});

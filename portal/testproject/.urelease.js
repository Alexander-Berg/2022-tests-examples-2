module.exports = {
    sandbox: {
        owner: 'HOME'
    },
    repo: {
        projectRoot: '.'
    },
    components: {
        res: {
            root: '.',
            command: 'mkdir resfiles && echo "test resource" > resfiles/res.txt',
            deploy: function ({version}) {
                const s3root = 'home-beta';

                return [
                    {
                        path: 'resfiles/',
                        resource: 'TRENDBOX_CI_REPORT_RESOURCE_BETA'
                    },
                    {
                        path: 'resfiles/',
                        s3path: `${s3root}/testproject/${version}`
                    }
                ]
            },
            files: [
                '!ci/**',
                '!package.json',
                '!package-lock.json'
            ]
        },
        env: {
            root: '.',
            command: 'mkdir envfiles && echo "test resource2" > envfiles/res.txt',
            deploy: function () {
                return [
                    {
                        path: 'envfiles/',
                        resource: 'TASK_LOGS'
                    }
                ];
            },
            files: [
                '.urelease.js',
                'package.json',
                'package-lock.json',
            ]
        }
    },
    projects: {
        testproject: {
            components: ["res", "env"],
            startrek: {
                releaseQueue: 'HOME',
                linkFilter: task => {
                    return task.queue.key === 'HOME' ||
                        (task.components || [])
                            .some(c => c.display === 'morda')
                },
                links: [
                ],
                skip: ["postponed", "deploying"]
            },
            webhooks: [
                'https://webhooks.potato.yandex.net/webhooks/' +
                    'github-enterprise/morda/main/service/nanny'
            ]

        }
    }
};

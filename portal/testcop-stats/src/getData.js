const fetch = require('node-fetch');

const projects = [
    {
        project: 'home',
        tools: [
            'hermione',
            'hermione-e2e',
            'cypress-e2e',
        ]
    }
];

const getSkips = async (project, tool) => {
    const {TestcopAPI} = require('@yandex-int/testcop-api');
    const api = TestcopAPI.create('');
    const skipsBranch = 'dev';

    const skips = await api.getTestSkips({
        project: project.project,
        tool: tool,
        skipsBranch,
        flakyStatsBranch: 'dev',
        isFlakyTestsStatsRequired: true,
    });
    for (const key of Object.keys(skips.skips)) {
        const splitKey = key.split('.');
        skips.skips[key].browserId = splitKey.pop();
        skips.skips[key].fullName = splitKey.join('.');
    }
    for (const key of Object.keys(skips.mutes)) {
        const splitKey = key.split('.');
        skips.mutes[key].browserId = splitKey.pop();
        skips.mutes[key].fullName = splitKey.join('.');
        skips.mutes[key].muted = true;
    }
    const skipsAndMutes = [...Object.values(skips.skips), ...Object.values(skips.mutes)];
    await writeData(project.project, tool, skipsAndMutes);
};
console.log('stating...');
(async () => {
    for (const project of projects) {
        console.log('fetching ', project);
        for (const tool of project.tools) {
            await getSkips(project, tool);
        }
    }
})();

const writeData = (() => {
    const yt = require('@yandex-data-ui/yt-javascript-wrapper')();
    yt.setup.setGlobalOption('proxy', 'hahn.yt.yandex-team.ru');

    return async (project, tool, skipsAndMutes) => {
        try {
            const byBrowsers = {};
            for (const v of skipsAndMutes) {
                if (!byBrowsers[v.browserId]) {
                    byBrowsers[v.browserId] = {muted: 0, skips: 0};
                }
                if (v.muted) {
                    byBrowsers[v.browserId].muted += 1;
                } else {
                    const m = byBrowsers[v.browserId].skips;
                    byBrowsers[v.browserId].skips += 1;
                }
            }
            for (const [browserId, {skips, muted}] of Object.entries(byBrowsers)) {
                await yt.v3.insertRows({
                    setup: {
                        authentication: {
                            type: 'oauth',
                            token: process.env.YT_OAUTH_TOKEN,
                        }
                    },
                    parameters: {
                        path: '//home/morda/mikstime/testcop',
                    },
                    data: [{
                        time: Date.now(), project, tool, skips, mutes: muted, browserId
                    }],
                });
            }
            console.log('Сохранены данные для ', project, '/', tool);
        } catch (e) {
            console.log(e);
        }
    };
})();

const path = require('path');
const fs = require('fs');
const vm = require('vm');
const fg = require('./fixture-generator');
const fixtures = new Map();

const [convertFileName, convertFixtureName] = (() => {
    const fileTesters = [
        [/^(i-|important-)/, 'important'],
        [/^(g-|groups-)/, 'groups'],
        [/^(t-|tabs-)/, 'tabs'],
        [/^(s-|settings-)/, 'settings'],
        [/^(n-|notification-)/, 'notification'],
    ];
    const convert = (postfix, file) => {
        let match;
        for (const test of fileTesters) {
            if (test[0].test(file)) {
                match = test;
                break;
            }
        }
        return match ? file.replace(match[0], match[1] + postfix) : file;
    };
    return [file => convert('/', file), fixture => convert('-', fixture)];
})();

function reloadFixture(name, file) {
    /* eslint-disable-next-line no-console */
    console.log('reloading fixture', name);
    let content = fs.readFileSync(file, 'utf-8');

    const context = {
        module: {
            exports: () => {},
        },
        ...fg,
    };
    vm.runInNewContext(`((__dirname) => {
        ${content}
    })(${JSON.stringify(path.dirname(file))})`, context);
    fixtures.set(name, context.module.exports);
}

function getModule(name) {
    const file = path.normalize(name);
    if (file.startsWith('..')) {
        throw new RangeError(`.. is forbidden for ${name}`);
    }
    name = convertFixtureName(name);
    if (!fixtures.has(name)) {
        const filename = path.resolve(__dirname + '/fixtures', `${convertFileName(name)}.js`);
        reloadFixture(name, filename);
        fs.watch(filename, () => reloadFixture(name, filename));
    }

    return fixtures.get(name);
}

module.exports = {
    name: 'fixture-runner',
    fn: function fixtureRunner(req, res, next) {
        const { query, kotik: { ctx } } = req;

        const { fixture } = query;
        if (!fixture) {
            return next();
        }

        try {
            const module = getModule(fixture);

            const mock = JSON.stringify(module(req));

            const mockedResponse = {
                type: 'http_response_json',
                statuscode: 200,
                headers: [
                    {
                        name: 'Content-Type',
                        value: 'application/json',
                    },
                    {
                        name: 'Content-Length',
                        value: mock.length,
                    },
                ],
                content: mock,
            };

            let backendRes = ctx.getOnlyItem('gnc_notifications_http_response');
            if (backendRes) {
                backendRes.binary = mockedResponse;
            } else {
                /* всё-равно собирались подменить */
                /* TODO: Что-то в котике идёт не так, и в рендерере
                 * возвращается не то, что нужно, а дебаггер не работает

                const source = ctx.getSourcesData()[0];
                source.data.answers.splice(6, 0, {
                    name: 'GNC_NOTIFICATIONS_POST',
                    results: [{
                        type: 'gnc_notifications_http_response',
                        binary: mockedResponse,
                        codec: 'lz4',
                    }],
                });
                */
                throw new Error('no backend response');
            }

            next();
        } catch (e) {
            try {
                const params = ctx.getOnlyItem('app_host_params');
                e.message += '\nReqid: ' + params.binary.reqid;
            } catch (err) {}
            next(e);
        }
    },
};

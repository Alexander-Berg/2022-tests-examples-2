const fs = require('fs');
const axios = require('axios').default;
const allureWriter = require('@shelex/cypress-allure-plugin/writer');

module.exports = (on, config) => {
    allureWriter(on, config);
    on('task', {
        readFileMaybe(filename) {
            if (fs.existsSync(filename)) {
                const contents = fs.readFileSync(filename, 'utf8');
                return contents ? JSON.parse(contents) : {};
            }
            return {};
        }
    });
    on('after:run', async results => {
        if (results) {
            // results will be undefined in interactive mode
            let body = {
                title: 'test run ' + results.startedTestsAt,
                testGroups: [],
                status: 'FINISHED',
                tags: ['autotest']
            };
            for (let run of results.runs) {
                let testGroup = {path: [run.spec.name], testCases: []};
                for (let test of run.tests) {
                    const testCaseId = test.title[test.title.length - 1].match(/(?<=corptaxi-)\d+/);
                    if (testCaseId) {
                        const id = +testCaseId[0];
                        await axios({
                            method: 'get',
                            url: `https://testpalm-api.yandex-team.ru/testcases/corptaxi?id=${id}`,
                            data: body,
                            headers: {
                                Authorization: `OAuth ${process.env.YAV_TOKEN}`,
                                'content-type': 'application/json'
                            }
                        })
                            .then(function (response) {
                                response = response.data[0];
                                let testStatus;
                                if (test.state === 'passed') testStatus = 'PASSED';
                                else if (test.state === 'failed') testStatus = 'FAILED';
                                else testStatus = 'SKIPPED';
                                let testCase = {
                                    testCase: {
                                        id: id,
                                        name: response.name,
                                        description: response.description,
                                        stepsExpects: response.stepsExpects,
                                        preconditions: response.preconditions,
                                        preconditionsFormatted: response.preconditionsFormatted,
                                        sharedPreconditions: response.sharedPreconditions,
                                        attributes: response.attributes
                                    },
                                    status: testStatus
                                };

                                testGroup.testCases.push(testCase);
                            })
                            .catch(function (error) {
                                console.log('Скорее всего опечатка в номере кейса. Testcase id - ' + id)
                                console.log(error);
                            });
                    }
                }
                body.testGroups.push(testGroup);
            }
            await axios({
                method: 'post',
                url: 'https://testpalm-api.yandex-team.ru/testrun/corptaxi/create',
                data: body,
                headers: {
                    Authorization: `OAuth ${process.env.YAV_TOKEN}`,
                    'content-type': 'application/json'
                }
            })
                .then(function (response) {
                    console.log('Testrun created!');
                    console.log(
                        'https://testpalm.yandex-team.ru/corptaxi/testrun/' + response.data[0].id
                    );
                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    });

    if (process.env.ENVIRONMENT === 'unstable') {
        config.baseUrl = 'https://corp-client.taxi.dev.yandex.ru';
        console.log('Run tests on unstable');
    } else {
        console.log('Run tests on testing');
    }

    on('task', {
        log(message) {
            console.log(message);
            return null;
        }
    });

    config.env.yavOauthToken = process.env.YAV_TOKEN;
    return config;
};

/* eslint no-console:0 */
const {
    createWorkflow
} = require('urelease');
const options = require('nopt')({
    ref: String,
    version: String,
    prevRef: String
});
const project = 'testproject';
const {
    ref,
    version,
    prevRef
} = options;

console.log(`ref (${ref})\nversion (${version})\nprevRef (${prevRef})`);

if (!ref  || !version) {
    console.error(`no ref (${ref}) || version (${version})`);
    process.exit(2);
}

const workflow = createWorkflow({
    project,
    version,
    ref,
    prevRef
})
    .withTkitParams({
        repo: {},
        resourcesDir: process.env.RESULT_RESOURCES_PATH + '/urelease',
        stopOnUpdate: false
    })
    .withTelegram({
        chat: 'home/core'
    })
    .withReleaseTicket({
    })
    /* порядок важен, сначала s3
     * https://st.yandex-team.ru/HOME-62789
     */
    .withS3Deploy({})
    .justBuildResources({});

workflow
    .getTicket()
    .getKey()
    .then(key => {
        const path = require('path');
        const fs = require('fs');
        if (!key) {
            throw new TypeError('Нет номера релизного таска');
        }
        const badgesPath = process.env.RESULT_BADGES_PATH;
        const resourcesPath = process.env.RESULT_RESOURCES_PATH;

        if (!badgesPath || !resourcesPath) {
            throw new Error(`Нет переменной RESULT_BADGES_PATH (${badgesPath}) или RESULT_RESOURCES_PATH (${resourcesPath}), добавьте result_badges в a.yaml`);
        }
        const paramsFile = path.resolve(resourcesPath, 'key');
        const badgesFile = path.resolve(badgesPath, 'badges');


        fs.writeFileSync(paramsFile, key);
        console.log(`Записан выходной параметр "${key}" в ${paramsFile}`);

        fs.writeFileSync(badgesFile, JSON.stringify({
            id: 'startrek',
            module: 'STARTREK',
            url: `https://st.yandex-team.ru/${key}`,
            text: 'Релизный таск',
            status: 'SUCCESSFUL'
        }));
        console.log(`Записан ci бейдж ${key} в ${badgesFile}`);
    })
    .catch(e => {
        console.error('Не удалось создать ci бейдж:', e);
        process.exit(15);
    });

workflow
    .start()
    .catch(e => {
        console.error(e);
        console.log('waiting 5 minutes...');
        setTimeout(() => process.exit(1), 5 * 60 * 1000);
    });

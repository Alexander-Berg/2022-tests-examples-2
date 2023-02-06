// eslint-disable-next-line import/no-unresolved
const { spawnAsPromised } = require('../../scripts/utils/proc');

const toJSON = (fn) => {
    return async (...args) => {
        let rawData;
        try {
            rawData = await fn(...args);
        } catch (e) {
            console.log(e);
            return;
        }
        try {
            rawData = JSON.parse(rawData);
        } catch (e) {
            console.log(`info "${args}"`);
            console.log(e);
        }
        if (!rawData) {
            throw new Error('Empty');
        }
        // eslint-disable-next-line consistent-return
        return rawData;
    };
};

module.exports = {
    last: toJSON(async (version) => {
        console.log(`version "${version}"`);
        return spawnAsPromised('ya', [
            'vault',
            'get',
            'version',
            version,
            '-j',
        ]);
    }),
    versionList: toJSON(async (secretId) => {
        console.log(`secret "${secretId}"`);
        return spawnAsPromised('ya', [
            'vault',
            'get',
            'secret',
            secretId,
            '-j',
        ]);
    }),
};

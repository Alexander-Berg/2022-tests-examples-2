const fs = require('fs');
const axios = require('axios').default;

async function readFileMaybe(filename) {
    if (fs.existsSync(filename)) {
        const contents = fs.readFileSync(filename, 'utf8');
        return contents ? JSON.parse(contents) : {};
    }
    return {};
}

module.exports = async usersFile => {
    let secretId = 'sec-01fbpj99ysgccb7fjx6vr4j5v1';

    if (!fs.existsSync(usersFile)) {
        console.log('Get Users file from yav');
        await axios({
            method: 'get',
            url: `https://vault-api.passport.yandex.net/1/versions/${secretId}/`,
            headers: {
                Authorization: `OAuth ${process.env.YAV_TOKEN}`
            }
        })
            .then(function (response) {
                fs.writeFileSync(usersFile, response.data.version.value[0].value);
            })
            .catch(function (error) {
                console.log(error);
            });
    }
    return await readFileMaybe(usersFile);
};

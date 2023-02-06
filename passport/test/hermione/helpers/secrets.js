const tokenator = require('@yandex-int/tokenator');
const {VaultClient} = require('@yandex-int/vault-client');

async function vault(secretId) {
    const tokenatorTokens = await tokenator(['vault']);

    // rejectUnauthorized для подавления ошибки - RequestError: self signed certificate in certificate chain
    const vaultClient = new VaultClient(tokenatorTokens.vault, {}, {rejectUnauthorized: false});

    let tokens;

    try {
        tokens = await vaultClient.getVersion(secretId);
    } catch (e) {
        if (e.message.startsWith('Response code 401')) {
            throw new Error(`Нет доступа в секретницу. https://yav.yandex-team.ru/secret/${secretId}/explore/versions`);
        }
        throw e;
    }

    return tokens.reduce((memo, token) => {
        memo[token.key] = token.value;
        return memo;
    }, {});
}

async function getToken(secretId, secretKeyName) {
    const tokens = await vault(secretId);

    return tokens[secretKeyName];
}

module.exports = {
    getToken
};

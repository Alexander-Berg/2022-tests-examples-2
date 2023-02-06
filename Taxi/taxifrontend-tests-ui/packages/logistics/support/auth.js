const {TUSClient} = require('@yandex-int/tus-client');

async function authorize(login) {
    const client = new TUSClient(process.env.TUS_TOKEN);
    const user = await client.getAccount({
        env: 'test',
        tus_consumer: 'logistic-test',
        login: login
    });
    await browser.$('[id="login"]', 10000).setValue(user.account.login);
    await browser.$('[id="passwd"]').setValue(user.account.password);
    await browser.$('[type="submit"]').click();
}

module.exports.authorize = authorize;

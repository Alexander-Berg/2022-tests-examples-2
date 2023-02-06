const retries = Number.isNaN(+process.env.RETRIES)
    ? 4
    : parseInt(process.env.RETRIES, 10);

const asyncConfig = JSON.parse(process.env.YA_SELENIUM_CONF);

const surfwaxHostname = 'sw.yandex-team.ru';
const gridUrl = `http://metrika@${surfwaxHostname}:80/v0`;

module.exports = {
    asyncConfig,
    retries,
    gridUrl,
    plugins: {
        '@yandex-int/hermione-surfwax-router': {
            enabled: Boolean(process.env.CI_SYSTEM),
            surfwaxHostname,
        },
    },
};

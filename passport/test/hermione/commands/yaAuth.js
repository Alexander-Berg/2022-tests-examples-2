const {User} = require('../helpers/user');
const {authorize} = require('../utils/authorization');
const {getPassportFrontendHost} = require(`../testEnvironmentConfig`);

/**
 * Авторизуемся на домене Паспорта аккаунтом из TUS или созданным в автотестах
 */
module.exports.yaAuth = async function(user) {
    // передали логин аккаунта из TUS или логин несуществующего аккаунта, который нужно создать
    if (typeof user === 'string') {
        await this.auth(user, {tld: process.env.TEST_TLD});
        // передали аккаунт, созданный в автотестах
    } else if (user instanceof User) {
        await authorize(this, getPassportFrontendHost(), user.login, user.password);
    } else {
        throw Error(`Неизвестный тип для аргумента user: ${user}`);
    }
};

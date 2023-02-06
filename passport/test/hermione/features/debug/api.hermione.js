const steps = require('../../helpers/api/steps');
const {userWithLogin} = require('../../helpers/user');
const {commonUser} = require('../../utils/utils');

/**
 * Тесты на тесты: базовые сценарии для api
 */
hermione.only.in('chrome-desktop'); // Не зависит от браузера
describe('debug/api-tests', function() {
    it('Получаем данные об аккаунте по uid из ЧЯ', async function() {
        const userinfo = await steps.blackbox.userinfo.getUserinfo(commonUser); // явный вызов userinfo

        assert.equal(userinfo['login'], commonUser.login);
    });
    it('Получаем данные об аккаунте по login из ЧЯ', async function() {
        const user = await userWithLogin(commonUser.login).fetchUserinfo(); // вызов userinfo через объект типа User

        assert.equal(user.uid, commonUser.uid);
    });

    it('Регистрируем портальный аккаунт без средств восстановления', async function() {
        const user = await steps.passport.registration.createEmptyUser();

        assert.isNotEmpty(user.uid, 'Значение uid после регистрации не должно быть пустым');
    });

    it('Регистрируем портальный аккаунт с кв-ко', async function() {
        const user = await steps.passport.registration.createUserWithControlQuestion();

        assert.isNotEmpty(user.uid, 'Значение uid после регистрации не должно быть пустым');
    });

    it('Регистрируем портальный аккаунт с защищённым телефоном', async function() {
        const user = await steps.passport.registration.createUserWithPhone();

        assert.isNotEmpty(user.uid, 'Значение uid после регистрации не должно быть пустым');
    });

    it('Привязываем защищённый телефон', async function() {});

    it('Привязываем незащищённый телефон', async function() {});

    it('Привязываем email для восстановления', async function() {});

    it('Привязываем email для уведомлений', async function() {});

    it('Привязываем email для сбора писем', async function() {});

    it('Создаём трек и читаем его содержимое', async function() {
        const trackId = await steps.passport.track.createTrack();
        const trackData = await steps.passport.track.readTrack(trackId);

        assert.property(trackData, 'track_type', 'register', 'По умолчанию должен создаваться трек с типом register');
    });
});

const El = require('@yandex-int/bem-page-object').Entity;

const magicBookPage = new El('.MagicBookPage');

magicBookPage.qr = new El('.MagicField-qr');
magicBookPage.error = new El('.MagicField-error');

const captchaScreen = new El('.CaptchaScreen');

captchaScreen.image = new El('.captcha img');
captchaScreen.input = new El('[data-t="field:input-captcha"]');
captchaScreen.key = new El('[name="captcha_key"]');
captchaScreen.button = new El('[data-t="button:action"]');

const authAccountListScreen = new El('.AuthAccountList');

authAccountListScreen.addButton = new El('[data-t="account-list-item-add"]');
authAccountListScreen.listButton = new El('[data-t="account-list-item-menu"]');

const contextMenu = new El('.ContextMenu');

contextMenu.firstContextItem = new El('.ContextMenu-button:nth-child(1)');

module.exports = {
    authAccountListScreen,
    magicBookPage,
    captchaScreen,
    contextMenu
};

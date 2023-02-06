const El = require('@yandex-int/bem-page-object').Entity;

const authSocialBlock = new El('.AuthSocialBlock');

authSocialBlock.providerPrimaryFB = new El('[data-t="provider:primary:fb"]');
authSocialBlock.socialProviderWithText = new El('.AuthSocialBlock-provider_withText');
authSocialBlock.moreBtn = new El('[data-t="provider:more"]');

const authSocialBlockSecondaryProviders = new El('.AuthSocialBlock-secondaryProviders');

authSocialBlockSecondaryProviders.moreBtn = new El('[data-t="provider:primary:mr"]');

const socialSuggestPage = new El('.SocialSuggestPage');

socialSuggestPage.registerButton = new El('[data-t="button:action:register-button"]');

const SocialSuggestRegisterSocial = new El('.SocialSuggestRegisterSocial');

SocialSuggestRegisterSocial.registerButton = new El('button');

const socialModeChoose = new El('#mode-choose');

socialModeChoose.profile = new El('.s-profile');

const pageOverlay = new El('.passp-page-overlay');

pageOverlay.loader = new El('.passp-page-overlay__loader');

const accountsScreen = new El('.Accounts');

const listScreen = new El('[data-t="page:list"]');

listScreen.listItemAddButton = new El('[data-t="account-list-item-add"]');

const domik = new El('.domik');

domik.social = new El('.domik-scl');
domik.social.iconFB = new El('.scl-icon_fb');

module.exports = {
    accountsScreen,
    authSocialBlock,
    authSocialBlockSecondaryProviders,
    domik,
    socialSuggestPage,
    SocialSuggestRegisterSocial,
    socialModeChoose,
    pageOverlay,
    listScreen
};

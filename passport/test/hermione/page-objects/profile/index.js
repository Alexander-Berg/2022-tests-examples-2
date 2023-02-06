const {Entity} = require('@yandex-int/bem-page-object');

const addProfile = new Entity('.s-add-profiles');

addProfile.socialIconFB = new Entity('.social-icon_fb');

const sectionSocial = new Entity('.Section.p-social');

sectionSocial.link = new Entity('[data-t="link:default"]');

const sectionSocialModal = new Entity('[data-t="modal:social-block"]');

module.exports = {
    addProfile,
    sectionSocial,
    sectionSocialModal
};

const pageObject = require('@yandex-int/bem-page-object');

module.exports = {
    loadPageObject(platform) {
        const elems = require(`./${platform}`);

        return pageObject.create(elems);
    }
};

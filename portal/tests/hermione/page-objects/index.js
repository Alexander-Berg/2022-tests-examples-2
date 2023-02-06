const pageObject = require('@yandex-int/bem-page-object');

module.exports = {
    loadPageObject(platform) {
        const elems = {
            ...require('./common'),
        };

        try {
            Object.assign(elems, require(`./${platform}`));
        } catch (error) {
            if (error.code !== 'MODULE_NOT_FOUND') {
                throw error;
            }
        }

        return pageObject.create(elems);
    },
};

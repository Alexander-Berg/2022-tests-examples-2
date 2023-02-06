const { Entity } = require('@yandex-int/bem-page-object');

module.exports = class ReactEntity extends Entity {
    static preset() {
        return 'react';
    }
};

import { Policies } from 'csp-header';
import { TLD } from 'express-yandex-csp';

const policies: Policies = {
    'script-src': [`pass-test.yandex.${TLD}`, 'social.yandex.ru'],
};

export default policies;

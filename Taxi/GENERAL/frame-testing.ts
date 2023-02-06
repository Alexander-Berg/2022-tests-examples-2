import {Policies} from 'csp-header';

const policies: Policies = {
    'frame-ancestors': [
        'self',
        'https://helpnearby.taxi.tst.yandex.ru',
        'https://helpnearby.taxi.dev.yandex.ru/',
        'https://helpnearby-unstable-01.taxi.dev.yandex.ru',
        'https://helpnearby-unstable-02.taxi.dev.yandex.ru',
        'https://helpnearby-unstable-03.taxi.dev.yandex.ru',
        'https://helpnearby-unstable-04.taxi.dev.yandex.ru',
        'https://localhost.msup.yandex.ru:8081',
    ],
    'frame-src': [
        'self',
        'https://helpnearby.taxi.tst.yandex.ru',
        'https://helpnearby.taxi.dev.yandex.ru/',
        'https://helpnearby-unstable-01.taxi.dev.yandex.ru',
        'https://helpnearby-unstable-02.taxi.dev.yandex.ru',
        'https://helpnearby-unstable-03.taxi.dev.yandex.ru',
        'https://helpnearby-unstable-04.taxi.dev.yandex.ru',
        'https://localhost.msup.yandex.ru:8081',
    ],
};

export default policies;

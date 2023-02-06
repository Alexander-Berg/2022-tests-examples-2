import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { AlertCommon } from '@block/alert-common/alert-common.view';

export function alertCommon() {
    return execView(AlertCommon, {
        item: {
            id: undefined,
            type: 'common',
            title: 'фидбек',
            subtitle: 'подзаголовок',
            url: 'https://yandex.ru',
            icon: 'feedback',
            body: 'Оставьте нам свой фидбек',
            log_url: 'https://yabs.yandex.ru/count/1615/7992190891386871591',
        },
        index: 0
    }, mockReq({}));
}

import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { MobileBalloon } from './mobile-balloon.view';

export const simple = () => {
    return execView(MobileBalloon, {}, mockReq({}, {
        RestoreMobileBalloon: {
            close_url: 'https://yabs.yandex.ru/count/814/1884343862',
            url: 'https://yandex.ru/portal/set/any/?sk=u8dd7e62e56db4ff04831489e2f8e885b&big_version=&retpath=https%3A%2F%2Fyandex.ru%2F'
        }
    })) +
    <script>{'$("*").click(function () {return false;});'}</script>;
};

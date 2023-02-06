import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { SmallPromo } from './small-promo.view';

let promo = {
    Distrib_small: {
        close_url: '/empty',
        counter: 'disaster3',
        product: 'app',
        show: 1,
        show_url: '/empty',
        text: 'Откройте в приложении',
        theme: 'light',
        url: '/empty'
    }
};

let appLightData = JSON.parse(JSON.stringify(promo));

let appDarkData = JSON.parse(JSON.stringify(promo));
appDarkData.Distrib_small.theme = 'dark';

let yabroLightData = JSON.parse(JSON.stringify(promo));
yabroLightData.Distrib_small.product = 'yabro';

let yabroDarkData = JSON.parse(JSON.stringify(yabroLightData));
yabroDarkData.Distrib_small.theme = 'dark';

let imgLightData = JSON.parse(JSON.stringify(yabroLightData));
imgLightData.Distrib_small.icon_app = 'https://avatars.mds.yandex.net/get-direct-picture/1674598/8cqjHHwcpLKkbdBKoaM6Kw/orig';

let imgDarkData = JSON.parse(JSON.stringify(imgLightData));
imgDarkData.Distrib_small.theme = 'dark';

export const appLight = () => execView(SmallPromo, {}, mockReq({}, appLightData));
export const appDark = () => execView(SmallPromo, {}, mockReq({}, appDarkData));
export const yabroLight = () => execView(SmallPromo, {}, mockReq({}, yabroLightData));
export const yabroDark = () => execView(SmallPromo, {}, mockReq({}, yabroDarkData));
export const imgLight = () => execView(SmallPromo, {}, mockReq({}, imgLightData));
export const imgDark = () => execView(SmallPromo, {}, mockReq({}, imgDarkData));

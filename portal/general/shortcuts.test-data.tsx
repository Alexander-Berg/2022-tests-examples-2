import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { ShortcutWeather } from '@block/shortcut-weather/shortcut-weather.view';
import { ShortcutRecent } from '@block/shortcut-recent/shortcut-recent.view';
import { ShortcutCommon } from '@block/shortcut-common/shortcut-common.view';
import { ShortcutMarket } from '@block/shortcut-market/shortcut-market.view';
import { Style } from '@block/common/common.view';

type ShortcutTemplate<T extends Req3AssistShortcutBase> = (
    data: {
        data: T;
        index: number;
    },
    req: Req3Server,
    execView: ExecViewCompat) =>
    {
        style: string;
        content: string;
    };

function createMock<T extends Req3AssistShortcutBase>(
    template: ShortcutTemplate<T>, data: T & { [k: string]: unknown }) {
    return function() {
        const req = mockReq();
        const shortcut = execView(template, {
            data,
            index: 0
        }, req);

        return '<div class="shortcut-wrapper" style="display: inline-block">' +
            execView(Style, { content: shortcut.style }, req) + shortcut.content +
            '</div>';
    };
}

export const weather = createMock<Req3AssistShortcutWeather>(
    ShortcutWeather,
    require('./mocks/weather.json')
);

export const mail = createMock<Req3AssistShortcutRecent>(
    ShortcutRecent,
    require('./mocks/mail.json')
);

export const service_active = createMock<Req3AssistShortcutRecent>(
    ShortcutRecent,
    require('./mocks/service_active.json')
);

export const common = createMock<Req3AssistShortcutCommon>(
    ShortcutCommon,
    require('./mocks/common.json')
);

export const market = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market.json')
);

export const market_coupon = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market_coupon.json')
);

export const market_itemDiscount = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market_itemDiscount.json')
);

export const market_itemDiscountMany = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market_itemDiscountMany.json')
);

export const market_itemDiscountPersonal = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market_itemDiscountPersonal.json')
);

export const market_priceDrop = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market_priceDrop.json')
);

export const market_priceDropMany = createMock<Req3AssistShortcutMarket>(
    ShortcutMarket,
    require('./mocks/market_priceDropMany.json')
);

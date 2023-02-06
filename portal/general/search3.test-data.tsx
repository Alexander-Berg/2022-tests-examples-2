import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Search3 } from '@block/search3/search3.view';

import emptyMock from './mocks/empty.json';
import aMock from './mocks/a.json';
import factMock from './mocks/fact.json';
import navMock from './mocks/nav.json';
import weatherMock from './mocks/weather.json';
import adMock from './mocks/ad.json';
import trafficMock from './mocks/traffic.json';
import fact2Mock from './mocks/fact2.json';
import ratesMock from './mocks/rates.json';
import empty2Mock from './mocks/empty2.json';

const ajaxMock = `<script>
var mocks = {
    '': ${JSON.stringify(emptyMock)},
    'a': ${JSON.stringify(aMock)},
    'длина': ${JSON.stringify(factMock)},
    'янд': ${JSON.stringify(navMock)},
    'погода': ${JSON.stringify(weatherMock)},
    'пробк': ${JSON.stringify(adMock)},
    'пробки': ${JSON.stringify(trafficMock)},
    'курс': ${JSON.stringify(fact2Mock)},
    'курс акций я': ${JSON.stringify(ratesMock)},
    'афыафафыафыа': ${JSON.stringify(empty2Mock)}
};

MBEM.blocks['mini-suggest'].prototype._request = function (text, callback) {
    if (text in mocks) {
        callback.call(this, text, mocks[text], '', 1);
    }
};
</script>`;

const imagesMock = `<style>
.mini-suggest__delete,
.mini-suggest__copy,
.mini-suggest__item-mark,
.mini-suggest__item-thumb {
    background:#ccc !important;
}
</style>`;

export function simple() {
    const req = mockReq({}, {
        ab_flags: {
            suggest_fact_carousel: {
                value: '1'
            },
            suggest_copy_fact: {
                value: '1'
            },
            direct_in_suggest: {
                value: '1'
            }
        }
    });

    return {
        html: ajaxMock + imagesMock +
            <div class="body__wrapper">
                <div class="content">
                    {execView(Search3, {}, req)}
                </div>
            </div>
    };
}

export function camera() {
    const req = mockReq({}, {
        ab_flags: {
            suggest_fact_carousel: {
                value: '1'
            },
            suggest_copy_fact: {
                value: '1'
            },
            direct_in_suggest: {
                value: '1'
            },
            touch_smart_camera: {
                value: '1'
            }
        },
        BrowserDesc: {
            isTouch: 1,
            BrowserEngine: 'WebKit',
            BrowserVersion: '13.0.3',
            isBrowser: 1,
            isMobile: 1,
            BrowserName: 'MobileSafari',
            OSFamily: 'iOS',
            BrowserBaseVersion: '604.1'
        }
    });

    return {
        html: ajaxMock + imagesMock +
            <div class="body__wrapper">
                <div class="content">
                    {execView(Search3, {}, req)}
                </div>
            </div>
    };
}

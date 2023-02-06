const {createSupchatStrategiesMap} = require('..');
const {createStrategyDefiner} = require('../../../createStrategyDefiner');
const {NoEncodeDecodeStrategy} = require('../../NoEncodeDecodeStrategy');
const {CallActionV1} = require('../v1/CallAction');
const {CreateTaskChatV2} = require('../v2/CreateTaskChat');
const {FetchDashboardTaskV1} = require('../v1/FetchDashboardTask');
const {GetTaskForSelectedLinesV1} = require('../v1/tasks/GetTaskForSelectedLines');
const {GetTaskV1} = require('../v1/tasks/GetTask');
const {RefreshTaskV1} = require('../v1/tasks/RefreshTask');
const {TakeTaskV1} = require('../v1/tasks/TakeTask');

const VALID_GET_URLS = [
    ['/chatterbox-api/v1/tasks/init?info=sdasdas', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/tasks/init/', NoEncodeDecodeStrategy],

    ['/chatterbox-api/v1/user/status', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/user/status/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/user/status?yandexId=12dasxeQX2', NoEncodeDecodeStrategy],

    ['/chatterbox-api/v1/tasks/dashboard/', FetchDashboardTaskV1],
    ['/chatterbox-api/v1/tasks/dashboard', FetchDashboardTaskV1],
    ['/chatterbox-api/v1/tasks/dashboard?lines=3&type=full', FetchDashboardTaskV1],

    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284', GetTaskV1],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/', GetTaskV1],

    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/take', RefreshTaskV1],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/take/', RefreshTaskV1],

    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/sip_url', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/sip_url/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/sip_url?uuid=sasd2sxcSSs2', NoEncodeDecodeStrategy],

    ['/chatterbox-api/v1/lines/612ca5d506d38e7e321b9284/options', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/lines/612ca5d506d38e7e321b9284/options/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/lines/612ca5d506d38e7e321b9284/options?show=all&force=true', NoEncodeDecodeStrategy],

    ['/chatterbox-api/v1/tasks/search/available_fields/', NoEncodeDecodeStrategy]
];

const VALID_POST_URLS = [
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/comment', CallActionV1],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/comment_with_tvm', CallActionV1],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/comment_with_tvm/', CallActionV1],

    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/take', TakeTaskV1],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/take/', TakeTaskV1],

    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/attachment?dr=asdasda', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/attachment/', NoEncodeDecodeStrategy],

    ['/chatterbox-api/v2/tasks/init/client', CreateTaskChatV2],
    ['/chatterbox-api/v2/tasks/init/driver', CreateTaskChatV2],
    ['/chatterbox-api/v2/tasks/init/client/', CreateTaskChatV2],

    ['/chatterbox-api/v1/tasks/take', GetTaskForSelectedLinesV1],

    ['/chatterbox-api/v1/tasks/search', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/user/status', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/user/incoming_sip', NoEncodeDecodeStrategy],
    ['/me', undefined],

    ['/chatterbox-api/v1/stat/online', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/stat/supporters_online/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/stat/realtime/supporters/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/stat/realtime/lines/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/stat/chats_by_status/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/stat/sip_calls/by_login/', NoEncodeDecodeStrategy],
    ['/chatterbox-api/v1/stat/offline/actions/', NoEncodeDecodeStrategy],

    ['/chatterbox-api/v1/tasks/612ca5d506d38e7e321b9284/add_to_meta', undefined],
    ['/chatterbox-api/v1/spellchecker', undefined]
];

const getStrategy = createStrategyDefiner(createSupchatStrategiesMap());

describe('POST urls', () => {
    test('strategies defines as expected', async () => {
        for (const [url, expectedStrategy] of VALID_POST_URLS) {
            const strategy = getStrategy({ method: 'POST', originalUrl: url});

            expect(
                (!strategy && !expectedStrategy) ||
                (expectedStrategy.constructor === strategy.constructor)
            );
        }
    });
});

describe('GET urls', () => {
    test('strategies defines as expected', async () => {
        for (const [url, expectedStrategy] of VALID_GET_URLS) {
            const strategy = getStrategy({ method: 'GET', originalUrl: url});

            expect(
                (!strategy && !expectedStrategy) ||
                (expectedStrategy.constructor === strategy.constructor)
            );
        }
    });
});

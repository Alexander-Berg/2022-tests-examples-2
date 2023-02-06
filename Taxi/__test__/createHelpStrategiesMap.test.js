const {createHelpStrategiesMap} = require('..');
const {createStrategyDefiner} = require('../../../createStrategyDefiner');
const {NoEncodeDecodeStrategy} = require('../../NoEncodeDecodeStrategy');
const { GetUserMessagesV1} = require('../v1/GetUserMessages');
const {AddMessageV2} = require('../v2/AddMessage');
const {CreateChatV2} = require('../v2/CreateChat');
const {GetChatV2} = require('../v2/GetChat');

const VALID_POST_URLS = [
    ['/support_chat/v2/chats/612ca5682df71229ae258780/message?service=taxi&handler_type=regular', AddMessageV2],
    ['/support_chat/v1/realtime/get_user_messages/?service=safety_center&handler_type=realtime', GetUserMessagesV1],
    ['/support_chat/v2/create_chat?service=corp&handler_type=realtime', CreateChatV2]
];
const VALID_GET_URLS = [
    ['/support_chat/v2/chats/60d5bf3c2df7121ffbf60e3c?service=drive', GetChatV2],
    ['/support_chat/v2/chats?services=drive%2Ceats%2Csafety_center%2Ctaxi&status=opened%2Cclosed&start_date=2021-07-25', NoEncodeDecodeStrategy],
    ['/support_chat/v2/configs?template=true&location=en', NoEncodeDecodeStrategy],
    ['/support_chat/v2/configs/', NoEncodeDecodeStrategy],
    ['/support_chat/v2/configs', NoEncodeDecodeStrategy],
    ['/support_chat/v1/realtime/read/60d5bf3c2df7121ffbf60e3c', NoEncodeDecodeStrategy],
    ['/support_chat/v1/realtime/read/60d5bf3c2df7121ffbf60e3c/', NoEncodeDecodeStrategy],
    ['/support_chat/v1/realtime/read/60d5bf3c2df7121ffbf60e3c?catalog=all', NoEncodeDecodeStrategy],
    ['/support_chat/v1/regular/read/60d5bf3c2df7121ffbf60e3c', NoEncodeDecodeStrategy]
];

const getStrategy = createStrategyDefiner(createHelpStrategiesMap());

describe('POST urls', () => {
    test('strategies defines as expected', () => {
        for (const [url, expectedStrategy] of VALID_POST_URLS) {
            const strategy = getStrategy({ method: 'POST', originalUrl: url});

            expect(
                (!strategy && !expectedStrategy) ||
                (strategy.constructor === expectedStrategy.constructor)
            );
        }
    });
});

describe('GET urls', () => {
    test('strategies defines as expected', () => {
        for (const [url, expectedStrategy] of VALID_GET_URLS) {
            const strategy = getStrategy({ method: 'GET', originalUrl: url});

            expect(
                (!strategy && !expectedStrategy) ||
                (strategy.constructor === expectedStrategy.constructor)
            );
        }
    });
});

const nhl = require('./mocks/nhl.json');
const story = require('./mocks/story.json');
const {Timestamp} = require('../../../common/blocks/stream/mocks/timestamp');

function wrap(content) {
    return `<style>
        html, body {
            margin: 0;
            padding: 0;
            background-color: #fff;
        }
        </style>
        <div class="root i-ua_browser_desktop">${content}</div>`;
}

const buildWidget = (data = {}, req = {}) => {
    const {settings = {}, exp = {}} = req;
    const reqData = Object.assign({}, {
        Stream: {
            settings: {...settings},
            front_base_url: 'https://frontend.vh.yandex.ru/v23'
        },
        Timestamp: Timestamp
    },
    data,
    {
        exp
    });

    return {
        data,
        req: reqData
    };
};

const exportsStorage = {
    simpleWidget: buildWidget({program: story, id: 'test_value', fromBlock: 'ether_embed_widget'}),
    simpleVideoWidget: buildWidget({program: story, id: 'test_value', isVideo: true, fromBlock: 'ether_embed_widget'}),
    nhlWidget: buildWidget({program: nhl, id: 'test_value', fromBlock: 'ether_embed_widget'})
};

for (const name in exportsStorage) {
    exports[name] = (execView) => {
        const {data, req} = exportsStorage[name];

        return wrap(execView.withReq('StreamWidget', data, req));
    };
}

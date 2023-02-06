import { execView } from '@lib/views/execView';
import { DirectTouch } from '@block/direct-touch/direct-touch.view';
import { mockReq } from '@lib/views/mockReq';
import { DirectDataResultTgo } from '@block/direct/__data/direct__data.view';

function getMock(path: string) {
    return {
        ...require(path),
        isTouch: true
    };
}
const styles = `<style>
    body {
        background-color: var(--color-g-bg-primary);
    }
    .direct-touch{
        height:102px;
        width:375px;
        margin: 0 !important;
    }
    .direct-touch__title{
        animation: none !important;
    }
    .direct-touch__body-text{
        animation: none !important;
    }
'</style>`;
const mocks = [
    {
        name: 'normal',
        mock: getMock('../direct/mocks/tgo.json')
    },
    {
        name: 'short',
        mock: getMock('../direct/mocks/tgo_short_text.json')
    },
    {
        name: 'warn',
        mock: getMock('../direct/mocks/tgo_warn.json')
    },
    {
        name: 'warnMed',
        mock: getMock('../direct/mocks/tgo_warn_med.json')
    },
    {
        name: 'socialAge',
        mock: {
            ...getMock('../direct/mocks/tgo.json'),
            isSocial: true
        }
    },
    {
        name: 'socialWarnMedAge',
        mock: {
            ...getMock('../direct/mocks/tgo_warn.json'),
            isSocial: true
        }
    }
];

const get = (directData: DirectDataResultTgo) => {
    const settingsJs = home.settingsJs([]);
    const req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        settingsJs
    });

    const banner = execView(DirectTouch, directData, req);

    const html = `
        ${styles}
        <script>${settingsJs.getRawScript(req)}</script>
        ${banner.html}
    `;

    return html;
};

mocks.forEach(mocks => {
    exports[mocks.name] = () => get(mocks.mock);
    exports[mocks.name + '_darkTheme'] = () => {
        return {
            html: get({ ...mocks.mock, darkTheme: true }),
            skin: 'night'
        };
    };
});

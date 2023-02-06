import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Search } from '@block/search2/search2.view';

export function simple() {
    const script = (
        <script>
            {`
    MBEM.blocks['mini-suggest'].prototype._request = function (text, callback) {
        window.respond = function (mock) {
            callback.call(this, text, mock, '', 1);
        }.bind(this);
    };

    $(function () {
        window.mocks = {
            y: ${JSON.stringify(require('./mocks/y.json'))},
            ya: ${JSON.stringify(require('./mocks/ya.json'))},
            yandex: ${JSON.stringify(require('./mocks/yandex.json'))},
            len: ${JSON.stringify(require('./mocks/len.json'))},
            weather: ${JSON.stringify(require('./mocks/weather.json'))},
            traffic: ${JSON.stringify(require('./mocks/traffic.json'))},
            flag: ${JSON.stringify(require('./mocks/flag.json'))},
            direct: ${JSON.stringify(require('./mocks/direct.json'))}
        };
    });

    $.ajax = function () {
        return $.Deferred();
    };
    `}
        </script>
    );

    const style = (
        <style>
            {`
        html, body {
            height: 100%;
        }

        .search2__placeholder{opacity: 0 !important};
        .mini-suggest__item-icon[style*=ovc-minus-ra] {
            background-image: url("data:image/svg+xml;charset=utf8,%3Csvg enable-background='new 0 0 32 32' viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M25.5 13.048c-.41 0-.806.06-1.185.163-.466-3.25-3.256-5.75-6.637-5.75-2.938 0-5.43 1.89-6.34 4.52l-.402-.02c-2.1 0-3.86 1.45-4.345 3.4l-.12-.01c-1.83 0-3.32 1.49-3.32 3.33 0 1.827 1.47 3.3 3.29 3.326h-.01 18.94l-.006-.01.137.01c2.48 0 4.48-2.005 4.48-4.477s-2-4.475-4.47-4.475zm-8.945 14.937l.005-4.078-3.218 2.808.016.007c-.192.166-.353.373-.47.616-.458.96-.05 2.11.914 2.57.963.463 2.116.06 2.575-.898.157-.332.213-.685.178-1.025z' fill='%237196EA' opacity='.7' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
        }
        .mini-suggest__item-icon[style*=bkn-d] {
            background-image: url("data:image/svg+xml;charset=utf8,%3Csvg enable-background='new 0 0 32 32' viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cpath d='M8.85 3c2.005.967 3.387 3.02 3.387 5.394 0 3.308-2.68 5.988-5.987 5.988-1.662 0-3.165-.678-4.25-1.77 1.11 2.06 3.29 3.46 5.795 3.46 3.633 0 6.58-2.945 6.58-6.578 0-3.274-2.393-5.99-5.524-6.494z' opacity='.8' fill='%23ED9700'/%3E%3Cpath d='M25.5 16.05c-.41 0-.806.06-1.185.163-.466-3.25-3.256-5.753-6.637-5.753-2.938 0-5.43 1.892-6.34 4.52l-.402-.02c-2.1 0-3.86 1.447-4.345 3.398l-.12-.013c-1.83 0-3.32 1.49-3.32 3.328 0 1.824 1.47 3.3 3.29 3.323L6.43 25h18.94l-.006-.008.137.008c2.48 0 4.48-2.004 4.48-4.476s-2-4.474-4.48-4.474z' opacity='.7' fill='%237196EA'/%3E%3C/g%3E%3C/svg%3E") !important;
        }
        .mini-suggest__item-icon[style*=traffic] {
            background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='33' height='33' viewBox='0 0 33 33'%3E%3Cpath fill='%234A8C16' d='M14.588 7.034c-.887.01-1.141.112-2.061.209-3.178.336-6.384 2.727-7.463 5.883-1.079 3.156-.09 5.066 3.825 5.066 1.41-.831 1.435-8.614 5.402-10.269.557-.233 1.118-.429 1.672-.586.267-.076.69-.24.69-.24s-.971-.076-2.065-.063z'/%3E%3Ccircle fill='%2366AB3C' cx='17.003' cy='17.073' r='9.976'/%3E%3Cpath fill='%23333' d='M17.032 7.074c-.87-.016-1.822-.07-3.347.085 4.065.167 7.811 2.414 9.322 7.124.464 1.551 2.469 3.463 3.924 3.581.027-.293.04-.59.04-.891 0-5.411-4.486-9.8-9.939-9.899z'/%3E%3C/svg%3E") !important;
        }
        .mini-suggest__item-icon[style*=russia] {
            background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='12' viewBox='0 0 16 12'%3E%3Cswitch%3E%3Cg%3E%3Cpath fill='%23FFF' d='M0 0h16v4H0z'/%3E%3Cpath fill='%23E03A3E' d='M0 8h16v4H0z'/%3E%3Cpath fill='%2300539F' d='M0 4h16v4H0z'/%3E%3C/g%3E%3C/switch%3E%3Cpath stroke='%23000' stroke-opacity='.2' fill='none' d='M0 0h16v12H0z'/%3E%3C/svg%3E") !important;
        }
        .mini-suggest__favicon {
            background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='12' viewBox='0 0 16 12'%3E%3Cswitch%3E%3Cg%3E%3Cpath fill='%23FFF' d='M0 0h16v4H0z'/%3E%3Cpath fill='%23E03A3E' d='M0 8h16v4H0z'/%3E%3Cpath fill='%2300539F' d='M0 4h16v4H0z'/%3E%3C/g%3E%3C/switch%3E%3Cpath stroke='%23000' stroke-opacity='.2' fill='none' d='M0 0h16v12H0z'/%3E%3C/svg%3E") !important;
        }
        `}
        </style>
    );

    const req = mockReq({}, {
        JSON: {
            searchParams: {},
            search: {
                url: '/'
            }
        },
        ClckBaseShort: 'yandex.ru/clck'
    });

    return script + style + execView(Search, {}, req);
}

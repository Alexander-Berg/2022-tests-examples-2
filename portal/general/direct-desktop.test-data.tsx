/* eslint-disable @typescript-eslint/ban-ts-comment */
import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { DirectDataResultTgo } from '@block/direct/__data/direct__data.view';
import { DirectDesktop } from '@block/direct-desktop/direct-desktop.view';
import * as tgoShortText from '@block/direct/mocks/tgo_short_text.json';
import * as tgoWarn from '@block/direct/mocks/tgo_warn.json';
import * as tgoWarnMed from '@block/direct/mocks/tgo_warn_med.json';
import * as tgo from '@block/direct/mocks/tgo.json';
import * as tgoButton from '@block/direct/mocks/tgo_button.json';
import * as tgoBUnit from '@block/direct/mocks/tgo_b_unit.json';

const styles = <style>
                {`
                    .direct-desktop{
                        height: 113px;
                        width: 918px;
                        margin: 20px;
                    }
                `}
               </style>;
const req: Req3Server = mockReq({}, {
    JSON: {
        common: {}
    }
});

function getBanner(mock: unknown) {
    const banner = execView(DirectDesktop, mock as DirectDataResultTgo, req);
    return styles + banner?.html + `<style> ${banner?.styles} </style>`;
}

export function bUnit() {
    return getBanner(tgoBUnit);
}
export function short() {
    return getBanner(tgoShortText);
}
export function warn() {
    return getBanner(tgoShortText);
}
export function socialAge() {
    return getBanner({ ...tgo, isSocial: true });
}
export function socialWarnMedAge() {
    return getBanner({ ...tgoWarn, isSocial: true });
}
export function button() {
    return getBanner({ ...tgoButton, buttonExp: true });
}

export function bUnit_dark() {
    return {
        html: getBanner(tgoBUnit),
        skin: 'night'
    };
}

export function short_dark() {
    return {
        html: getBanner(tgoShortText),
        skin: 'night'
    };
}
export function warn_dark() {
    return {
        html: getBanner(tgoShortText),
        skin: 'night'
    };
}
export function socialAge_dark() {
    return {
        html: getBanner({ ...tgo, isSocial: true }),
        skin: 'night'
    };
}
export function socialWarnMedAge_dark() {
    return {
        html: getBanner({ ...tgoWarnMed, isSocial: true }),
        skin: 'night'
    };
}

export function button_dark() {
    return {
        html: getBanner({ ...tgoButton, buttonExp: true }),
        skin: 'night'
    };
}

import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

import { SearchSelectPromoTop, SearchSelectPromoAfterSearch } from '@block/search-select-promo/search-select-promo.view';

import tooltipTopData from './mocks/tooltip-top.json';
import stripeTopData from './mocks/stripe.json';
import tooltipBottomData from './mocks/tooltip-bottom.json';
import arrowData from './mocks/arrow.json';
import arrowFullData from './mocks/arrow-full.json';

const renderTop = (data: Partial<Req3Server>) => {
    return execView(SearchSelectPromoTop, {}, mockReq({}, data));
};

const renderTopDark = (data: Partial<Req3Server>) => {
    return {
        html: execView(SearchSelectPromoTop, {}, { Skin: 'night', ...mockReq({}, data) }),
        skin: 'night'
    };
};

const renderAfterSearch = (data: Partial<Req3Server>) => {
    return execView(SearchSelectPromoAfterSearch, {}, mockReq({}, data));
};

const renderAfterSearchDark = (data: Partial<Req3Server>) => {
    return {
        html: execView(SearchSelectPromoAfterSearch, {}, { Skin: 'night', ...mockReq({}, data) }),
        skin: 'night'
    };
};

export function tooltipTop() {
    return renderTop(tooltipTopData as Partial<Req3Server>);
}

export function stripeTop() {
    return renderTop(stripeTopData as Partial<Req3Server>);
}

export function stripeTopDark() {
    return renderTopDark(stripeTopData as Partial<Req3Server>);
}

export function tooltipTopDark() {
    return renderTopDark(tooltipTopData as Partial<Req3Server>);
}

export function tooltipBottom() {
    return renderAfterSearch(tooltipBottomData as Partial<Req3Server>);
}

export function tooltipBottomDark() {
    return renderAfterSearchDark(tooltipBottomData as Partial<Req3Server>);
}

export function arrow() {
    return renderAfterSearch(arrowData as Partial<Req3Server>);
}

export function arrowDark() {
    return renderAfterSearchDark(arrowData as Partial<Req3Server>);
}

export function arrowFull() {
    return renderAfterSearch(arrowFullData as Partial<Req3Server>);
}

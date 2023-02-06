import * as chai from 'chai';
import { setElementId, getElementsCache } from '../global';

export const createNode = (
    tag = 'div',
    innerHtml = 'Hello',
    elIdProperty?: number,
) => {
    const div = document.createElement(tag);
    div.innerHTML = innerHtml;

    if (elIdProperty) {
        setElementId(div, elIdProperty);
        getElementsCache()[elIdProperty] = {
            pos: '100x100',
            size: '50x50',
        };
    }

    return div;
};

export const createSimpleDiv = (elIdProperty?: number) =>
    createNode('div', 'Hello World', elIdProperty);

export const createInputInForm = (elIdProperty?: number) => {
    const innerHTML = '<input />';
    return createNode('form', innerHTML, elIdProperty)
        .firstChild as HTMLElement;
};

export const assertByteCode = (
    a: number[] | undefined,
    b: number[] | undefined,
) => {
    chai.expect(a || []).to.be.deep.eq(b || []);
};

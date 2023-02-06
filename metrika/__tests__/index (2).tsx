import * as React from 'react';

import { render, configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import { isString, isNumber, isBoolean, isNull, isUndefined } from 'lodash';

import { deepMap } from '..';

configure({ adapter: new Adapter() });

const { isValidElement, cloneElement } = React;

describe('deepMap', () => {
    it('should visit every element', () => {
        const tree = (
            <div className="root">
                <span className="firstLevel">
                    <span className="secondLevel">
                        array of simple nodes
                        {1}
                        {true}
                        {null}
                        {undefined}
                    </span>
                </span>
            </div>
        );
        const out = deepMap(tree, (child) => {
            if (isValidElement<any>(child)) {
                return cloneElement(
                    child,
                    {
                        ...child.props,
                        className: `${child.props.className}-visited`,
                    },
                    child.props.children,
                );
            }

            return `${child} visited `;
        });
        const container = render(<div>{out}</div>);

        expect(container).toMatchSnapshot();
    });

    it('should handle string roots', () => {
        const out = deepMap('foo', (child) =>
            isString(child) ? child.toUpperCase() : child,
        );
        expect(out).toBe('FOO');
    });

    it('should handle string roots and transform them', () => {
        const tree = deepMap('foo foo foo', (child) =>
            isString(child)
                ? child
                      .split(' ')
                      // eslint-disable-next-line react/no-array-index-key
                      .map((str, index) => <span key={index}>{str}</span>)
                : child,
        );
        const container = render(<div>{tree}</div>);

        expect(container).toMatchSnapshot();
    });

    it('should handle number roots', () => {
        const out = deepMap(1, (child) =>
            isNumber(child) ? child + 1 : child,
        );
        expect(out).toBe(2);
    });
    it('should handle boolean roots', () => {
        const out = deepMap(true, (child) =>
            isBoolean(child) ? !child : child,
        );
        expect(out).toBe(false);
    });
    it('should handle null/undef roots', () => {
        const outNull = deepMap(null, (child) =>
            isNull(child) ? 'null' : child,
        );
        expect(outNull).toBe('null');

        const outUndef = deepMap(undefined, (child) =>
            isUndefined(child) ? 'undefined' : child,
        );
        expect(outUndef).toBe('undefined');
    });
});

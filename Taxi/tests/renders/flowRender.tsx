import {render} from '@testing-library/react';
import lodashFlow from 'lodash/flow';
import {ReactNode} from 'react';

type RenderFunction = (children: ReactNode, ...args: unknown[]) => ReactNode;

export function flow(
    children: ReactNode,
    functions: RenderFunction[],
) {
    return lodashFlow(functions)(children);
}

export function flowRender(
    children: ReactNode,
    functions: RenderFunction[],
    customRender: typeof render | ReturnType<typeof render>['rerender'] = render,
) {
    return customRender(flow(children, functions));
}

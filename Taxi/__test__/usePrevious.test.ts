import {renderHook} from '@testing-library/react-hooks';

import {usePrevious} from '..';

// TODO: TEWFM-906
test.skip('usePrevious shouldn`t return value on first render', async () => {
    const {result} = renderHook(({value}) => usePrevious(value), {
        initialProps: {
            value: 'test',
        },
    });

    expect(result.current).toBe(undefined);
});

// TODO: TEWFM-906
test.skip('usePrevious should return previous value after render', async () => {
    const {result, rerender} = renderHook(({value}) => usePrevious(value), {
        initialProps: {
            value: 5,
        },
    });

    rerender({value: 10});
    expect(result.current).toBe(5);
    rerender({value: 25});
    expect(result.current).toBe(10);
});

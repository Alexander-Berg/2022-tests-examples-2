import {renderHook} from '@testing-library/react-hooks';
import {useQuery} from 'react-query';

import {Wrapper} from 'utils/tests/renders';

function useCustomHook() {
    return useQuery('customHook', () => 'Hello');
}

describe('react-query example', () => {
    // TODO: TEWFM-906
    test.skip('react-query should return Hello', async () => {
        const {result, waitFor} = renderHook(() => useCustomHook(), {wrapper: Wrapper});

        await waitFor(() => result.current.isSuccess);
        expect(result.current.data).toEqual('Hello');
    });
});

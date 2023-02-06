import React from 'react';

import {useLocalStorage} from '..';

export default function Component() {
    const [value, setValue] = useLocalStorage('testUseLocalStorageHook', 'initial');

    return (
        <div>
            <div>{value}</div>
            <button onClick={() => setValue('test')}>Change value</button>
        </div>
    );
};

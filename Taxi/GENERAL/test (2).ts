import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import store from 'reduxStore';

export type Temp = {
    mapClicksCounter: number;
};

export const initialState: Temp = {
    mapClicksCounter: 0
};

const slice = createSlice({
    name: 'MAPPA/UI/TEST',
    initialState,
    reducers: {
        increment(state, action: PayloadAction<number>) {
            console.log('reducer payload', action.payload);

            return {
                mapClicksCounter: state.mapClicksCounter + 1
            };
        }
    }
});

export const {actions} = slice;

export const bound = store.bindActions<typeof actions>(actions);

export default slice.reducer;

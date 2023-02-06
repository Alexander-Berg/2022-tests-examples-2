import {isString} from 'lodash';
import {Moment} from 'moment';

import {Filters} from '_pkg/utils/getFilterFromUrl';
import {exact} from '_types/__test__/asserts';
import {DraftModes} from '_types/common/drafts';

import {useQuery} from '../use-query-params';

type QueryParams = {
    age?: number;
    date?: Moment;
    mode: DraftModes;
    name?: string;
    colors?: string[];
};

const isDraftMode = (value?: string | string[]): value is DraftModes => (
    isString(value) && Object.values(DraftModes).some(m => m === value)
);

describe('Проверка useQuery, useParams', () => {
    it('Вывод типа в useQuery без дефолта', () => {
        try {
            const filters: Filters<Assign<QueryParams, {mode?: DraftModes}>> = {
                age: Number,
                date: Date,
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : undefined,
                name: String,
                colors: Array,
            };

            const q1 = useQuery({
                age: Number,
                date: Date,
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : undefined,
                name: String,
                colors: Array,
            });

            const q2 = useQuery(filters);

            exact<typeof q1, Assign<QueryParams, {mode?: DraftModes}> & {__timestamp?: string}>(true);
            exact<typeof q1, typeof q2>(true);
        } catch {
            // ignore
        }
    });

    it('Вывод типа в useQuery с дефолтом', () => {
        try {
            type Params = {
                id?: string;
                mode: DraftModes;
            };

            const filters: Filters<Params> = {
                id: String,
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : DraftModes.Copy,
            };

            const q1 = useQuery({
                id: String,
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : DraftModes.Copy,
            });
            const q2 = useQuery(filters);
            exact<typeof q1, Params & {__timestamp?: string}>(true);
            exact<typeof q1, typeof q2>(true);
        } catch {
            // ignore
        }
    });
});

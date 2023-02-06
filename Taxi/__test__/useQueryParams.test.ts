import {isString} from 'lodash';
import {Moment} from 'moment';

import {arrayParser, momentParser, numberParser, ParamParsers, QueryParsers, stringParser} from '_pkg/utils/getFilterFromUrl';
import {exact} from '_types/__test__/asserts';
import {DraftModes} from '_types/common/drafts';

import {useParams, useQuery} from '../use-query-params';

type QueryParams = {
    age?: number;
    date?: Moment;
    mode: DraftModes;
    name?: string;
    colors?: string[];
};

type Params = {
    id: string;
    mode: DraftModes;
};

const isDraftMode = (value?: string | string[]): value is DraftModes => (
    isString(value) && Object.values(DraftModes).some(m => m === value)
);

describe('Проверка useQuery, useParams', () => {
    it('Вывод типа в useQuery без дефолта', () => {
        try {
            const filters: QueryParsers<Assign<QueryParams, {mode?: DraftModes}>> = {
                age: numberParser(),
                date: momentParser(),
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : undefined,
                name: stringParser(),
                colors: arrayParser(),
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

            const filters: QueryParsers<Params> = {
                id: stringParser(),
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : DraftModes.Copy,
            };

            const q1 = useQuery({
                id: stringParser(),
                mode: (mode?: string | string[]) => isDraftMode(mode) ? mode : DraftModes.Copy,
            });
            const q2 = useQuery(filters);
            exact<typeof q1, Params & {__timestamp?: string}>(true);
            exact<typeof q1, typeof q2>(true);
        } catch {
            // ignore
        }
    });

    it('Вывод типа в useParams без дефолта', () => {
        try {
            const parsers: ParamParsers<Partial<Params>> = {
                id: stringParser(),
                mode: stringParser<DraftModes>(),
            };
            const params = useParams(parsers);

            exact<typeof params, {
                id?: string;
                mode?: DraftModes
            }>(true);
        } catch {
            // ignore
        }
    });

    it('Вывод типа в useParams с дефолтом', () => {
        try {
            const parsers: ParamParsers<Params> = {
                id: stringParser('default'),
                mode: stringParser<DraftModes>(DraftModes.Copy)
            };
            const params = useParams(parsers);
            exact<typeof params, {mode: DraftModes, id: string}>(true);
        } catch {
            // ignore
        }
    });
});

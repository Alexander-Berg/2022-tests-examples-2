import {StageType} from '../../consts';
import {StageFetchView, StageGroupView, StageLogicView, StagePredicateView, StageTypeView} from '../../types';
import {getAllPrevStages} from '../prevStagesSelector';

const FETCH_STAGE: StageFetchView = {
    id: 'fetch_1',
    name: 'fetch',
    in_bindings: [],
    source_code: '',
    type: StageType.Fetch,
    conditions: [],
    resources: [],
};

const LOGIC_STAGE: StageLogicView = {
    id: 'logic_1',
    name: 'logic',
    in_bindings: [],
    source_code: '',
    type: StageType.Logic,
    conditions: [],
    out_bindings: [],
};

const PREDICATE_STAGE: StagePredicateView = {
    id: 'pred_1',
    name: 'pred',
    in_bindings: [],
    source_code: '',
    type: StageType.Predicate,
    args: [],
};

const DEFAULT_GROUP: StageGroupView = {
    name: '',
    id: 'gr_1',
    type: StageType.Group,
    conditions: [],
    stages: [],
};

describe('getAllPrevStages', () => {
    it('Формирование списка этапов из плоского списка', () => {
        const model: StageTypeView[] = [
            FETCH_STAGE,
            LOGIC_STAGE,
            PREDICATE_STAGE,
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        const expectedValue: StageTypeView[] = [
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        expect(getAllPrevStages('pred_1', model)).toEqual(expectedValue);
    });

    it('Формирование списка предыдущих этапов для группы', () => {
        const model: StageTypeView[] = [
            FETCH_STAGE,
            LOGIC_STAGE,
            PREDICATE_STAGE,
            DEFAULT_GROUP,
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        const expectedValue: StageTypeView[] = [
            FETCH_STAGE,
            LOGIC_STAGE,
            PREDICATE_STAGE,
        ];

        expect(getAllPrevStages('gr_1', model)).toEqual(expectedValue);
    });

    it('Многоуровневый список этапов для верхнего уровня', () => {
        const model: StageTypeView[] = [
            {
                ...DEFAULT_GROUP, stages: [
                    {
                        ...DEFAULT_GROUP, stages: [
                            FETCH_STAGE,
                            FETCH_STAGE,
                            FETCH_STAGE,
                        ]
                    },
                    LOGIC_STAGE,
                ]
            },
            PREDICATE_STAGE,
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        const expectedValue: StageTypeView[] = [
            FETCH_STAGE,
            FETCH_STAGE,
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        expect(getAllPrevStages('pred_1', model)).toEqual(expectedValue);
    });

    it('Многоуровневый список этапов для вложенного уровня', () => {
        const model: StageTypeView[] = [
            {
                ...DEFAULT_GROUP, stages: [
                    {
                        ...DEFAULT_GROUP, stages: [
                            FETCH_STAGE,
                            FETCH_STAGE,
                            FETCH_STAGE,
                        ]
                    },
                    LOGIC_STAGE,
                ]
            },
            {
                ...DEFAULT_GROUP, stages: [
                    LOGIC_STAGE,
                    {
                        ...DEFAULT_GROUP, stages: [
                            LOGIC_STAGE,
                            PREDICATE_STAGE,
                            FETCH_STAGE,
                            LOGIC_STAGE,
                        ]
                    },
                    FETCH_STAGE,
                    LOGIC_STAGE,
                ]
            },
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        const expectedValue: StageTypeView[] = [
            FETCH_STAGE,
            FETCH_STAGE,
            FETCH_STAGE,
            LOGIC_STAGE,
            LOGIC_STAGE,
            LOGIC_STAGE,
        ];

        expect(getAllPrevStages('pred_1', model)).toEqual(expectedValue);
    });

    it('Пустой список этапов', () => {
        const model: StageTypeView[] = [];

        expect(getAllPrevStages('pred_1', model)).toEqual([]);
    });

    it('Id отсутствует', () => {
        const model: StageTypeView[] = [
            FETCH_STAGE,
            LOGIC_STAGE,
            FETCH_STAGE,
            LOGIC_STAGE,
        ];

        expect(getAllPrevStages('pred_1', model)).toEqual([]);
    });
});

import {
    FileMethodTypes,
    PredicateArgTypes,
    PredicateArrayProps,
    PredicateInFileProps,
    PredicateMethods,
    PredicateSegmentationProps,
    PredicateTypes,
    RootPredicate
} from '_libs/experiment-predicates/types';

import {Clause} from '../../types';
import {buildControlGroup, getNeedToRemoveAnalyticalTag, hasAnalyticalPredicate} from '../clauseUtils';

const TRUE_PREDICATE: RootPredicate = {
    type: PredicateTypes.True,
    method: PredicateMethods.Interface,
    json: ''
};

const SEGMENTATION_PREDICATE: PredicateSegmentationProps = {
    type: PredicateTypes.Segmentation,
    init: {
        arg_name: 'hello',
        range_from: 0,
        range_to: 10,
        divisor: 100,
        salt: 'some_salt'
    },
    method: PredicateMethods.Interface,
    json: ''
};

const MOD_SHA_PREDICATE: PredicateSegmentationProps = {
    ...SEGMENTATION_PREDICATE,
    type: PredicateTypes.ModSha1WithSalt
};

const IN_FILE_PREDICATE: PredicateInFileProps = {
    type: PredicateTypes.Segmentation,
    init: {
        arg_name: 'hello',
        set_elem_type: PredicateArgTypes.String,
        uploadMethod: FileMethodTypes.UploadWithPartnerPhoneId,
        file: 'some_file',
        fileUpload: ''
    },
    method: PredicateMethods.Interface,
    json: ''
};

const NESTED_NOT_ANALYTICAL_PREDICATE: PredicateArrayProps = {
    type: PredicateTypes.AllOf,
    init: {
        predicates: [
            TRUE_PREDICATE,
            {
                type: PredicateTypes.Not,
                init: {
                    predicate: {
                        type: PredicateTypes.Bool,
                        init: {
                            arg_name: 'name',
                            value: 'true'
                        }
                    }
                }
            }
        ]
    },
    method: PredicateMethods.Interface,
    json: ''
};

const NESTED_ANALYTICAL_PREDICATE: PredicateArrayProps = {
    type: PredicateTypes.AllOf,
    init: {
        predicates: [
            {
                type: PredicateTypes.True,
            },
            {
                type: PredicateTypes.Segmentation,
                init: {
                    arg_name: 'hello',
                    range_from: 0,
                    range_to: 10,
                    divisor: 100,
                    salt: 'some_salt'
                }
            }
        ]
    },
    method: PredicateMethods.Interface,
    json: ''
};

const NESTED_ANALYTICAL_PREDICATE_WITH_TWO_SEGMENTATIONS: PredicateArrayProps = {
    type: PredicateTypes.AllOf,
    init: {
        predicates: [
            {
                type: PredicateTypes.Segmentation,
                init: {
                    arg_name: 'hello',
                    range_from: 0,
                    range_to: 10,
                    divisor: 100,
                    salt: 'some_salt'
                }
            },
            {
                type: PredicateTypes.Segmentation,
                init: {
                    arg_name: 'hello',
                    range_from: 90,
                    range_to: 100,
                    divisor: 100,
                    salt: 'some_salt'
                }
            }
        ]
    },
    method: PredicateMethods.Interface,
    json: ''
};

describe('utils/hasAnalyticalPredicate', () => {
    test('Должна вернуть false для простого неаналитического предиката', () => {
        expect(hasAnalyticalPredicate(TRUE_PREDICATE)).toBeFalsy();
    });
    test('Должна вернуть true для простого аналитического предиката', () => {
        expect(hasAnalyticalPredicate(SEGMENTATION_PREDICATE)).toBeTruthy();
        expect(hasAnalyticalPredicate(MOD_SHA_PREDICATE)).toBeTruthy();
        expect(hasAnalyticalPredicate(IN_FILE_PREDICATE)).toBeTruthy();
    });
    test('Должна вернуть false для неаналитического предиката с уровнем вложенности > 1', () => {
        expect(hasAnalyticalPredicate(NESTED_NOT_ANALYTICAL_PREDICATE)).toBeFalsy();
    });
    test('Должна вернуть true для аналитического предиката с уровнем вложенности > 1', () => {
        expect(hasAnalyticalPredicate(NESTED_ANALYTICAL_PREDICATE)).toBeTruthy();
    });
});

function generateClausesByPredicates(clauses: RequireKeys<Partial<Clause>, 'predicate'>[]) {
    return clauses.map((clause, index) => ({
        title: `${index + 1}`,
        value: '{}',
        enabled: true,
        is_tech_group: false,
        ...clause
    }));
}

describe('utils/getNeedToRemoveAnalyticalTag', () => {
    test('Должна вернуть true для неаналитических условий', () => {
        const clauses: Clause[] = generateClausesByPredicates([
            {
                predicate: TRUE_PREDICATE
            },
            {
                predicate: NESTED_NOT_ANALYTICAL_PREDICATE
            },
            {
                predicate: TRUE_PREDICATE
            }
        ]);

        expect(getNeedToRemoveAnalyticalTag(clauses)).toBeTruthy();
    });
    test('Должна вернуть true, если подходящих условий < 2', () => {
        const clauses: Clause[] = generateClausesByPredicates([
            {
                predicate: SEGMENTATION_PREDICATE
            },
            {
                predicate: NESTED_NOT_ANALYTICAL_PREDICATE
            },
            {
                predicate: TRUE_PREDICATE
            },
            {
                predicate: NESTED_ANALYTICAL_PREDICATE,
                is_tech_group: true
            },
            {
                predicate: NESTED_ANALYTICAL_PREDICATE,
                enabled: false
            }
        ]);

        expect(getNeedToRemoveAnalyticalTag(clauses)).toBeTruthy();
    });
    test('Должна вернуть false для подходящих условий > 1', () => {
        const clauses: Clause[] = generateClausesByPredicates([
            {
                predicate: SEGMENTATION_PREDICATE
            },
            {
                predicate: NESTED_NOT_ANALYTICAL_PREDICATE
            },
            {
                predicate: MOD_SHA_PREDICATE,
            },
        ]);

        expect(getNeedToRemoveAnalyticalTag(clauses)).toBeFalsy();
    });
    test('Должна вернуть false, если есть включенная нетехническая пара тестовой и контрольной группы', () => {
        const clauses: Clause[] = generateClausesByPredicates([
            {
                predicate: SEGMENTATION_PREDICATE,
                hasSignalClause: true
            },
        ]);
        const firstClause = clauses[0];
        const signalClause = buildControlGroup(firstClause);
        firstClause.signalClause = signalClause;

        expect(getNeedToRemoveAnalyticalTag(clauses)).toBeFalsy();
    });
    test('Должна вернуть true для одной группы', () => {
        const clauses: Clause[] = generateClausesByPredicates([
            {
                predicate: NESTED_ANALYTICAL_PREDICATE_WITH_TWO_SEGMENTATIONS,
            }
        ]);

        expect(getNeedToRemoveAnalyticalTag(clauses)).toBeTruthy();
    });
});

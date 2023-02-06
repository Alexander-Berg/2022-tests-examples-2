import {describe, expect, it} from 'tests/jest.globals';

import type {Rules} from 'types/role';

import {mergeRules} from './merge-rules';

describe('merge rules', () => {
    it('should merge rules', async () => {
        const suites: {rules: Rules[]; expected: Rules}[] = [
            {
                rules: [
                    {
                        product: {
                            canEditAttributeAll: true,
                            canNotEditAttribute: ['test', 'test2']
                        }
                    },
                    {
                        product: {
                            canEditAttributeAll: true,
                            canNotEditAttribute: ['test', 'test2', 'test3']
                        },
                        attribute: {
                            canEdit: true
                        }
                    }
                ],
                expected: {
                    product: {
                        canEditAttributeAll: true,
                        canNotEditAttribute: ['test', 'test2']
                    },
                    attribute: {
                        canEdit: true
                    }
                }
            },

            {
                rules: [{attribute: {canEdit: true}}, {canDebug: true}, {canBulk: true}],
                expected: {
                    attribute: {canEdit: true},
                    canDebug: true,
                    canBulk: true
                }
            },

            {
                rules: [
                    {product: {canEditAttribute: ['test1', 'test2']}},
                    {product: {canEditAttribute: ['test3']}},
                    {product: {canEditAttribute: ['test1', 'test4']}}
                ],
                expected: {product: {canEditAttribute: ['test1', 'test2', 'test3', 'test4']}}
            },

            {
                rules: [
                    {product: {canEditAttribute: ['test1', 'test2', 'test3'], canEditAttributeGroup: ['group1']}},
                    {
                        product: {
                            canEditAttributeAll: true,
                            canNotEditAttribute: ['test1', 'test2', 'test4'],
                            canNotEditAttributeGroup: ['group2']
                        }
                    }
                ],
                expected: {
                    product: {
                        canEditAttributeAll: true,
                        canNotEditAttribute: ['test4'],
                        canNotEditAttributeGroup: ['group2']
                    }
                }
            },

            {
                rules: [{product: {canEdit: true}}, {product: {canEditStatus: true}}],
                expected: {
                    product: {canEdit: true}
                }
            },

            {
                rules: [{product: {canEditAttribute: ['test']}}, {product: {canEditAttributeGroup: ['group']}}],
                expected: {
                    product: {
                        canEditAttribute: ['test'],
                        canEditAttributeGroup: ['group']
                    }
                }
            }
        ];

        for (const {rules, expected} of suites) {
            expect(mergeRules(rules)).toMatchObject(expected);
        }
    });
});

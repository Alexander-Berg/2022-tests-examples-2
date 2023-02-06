import {expect} from 'tests/jest.globals';

import {StepCode} from 'types/crm-candidates';

import {getUnusedNodes} from './utils';

describe('Candidate steps', () => {
    test('all vertices are connected', () => {
        const unusedNodes = getUnusedNodes(StepCode.N_1_1);
        expect(unusedNodes).toHaveLength(0);
    });
});

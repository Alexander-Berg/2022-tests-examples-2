import fs from 'fs';
import path from 'path';

import {cleanupFullImports, getFullImports, predicate, transform as lodashTransform} from '../transforms/lodash';
import transform, {} from '../utils/transform';

// tslint:disable-next-line: no-var-requires
const prettier = require('prettier');

const config = JSON.parse(
    fs.readFileSync(path.resolve(__dirname, `../../../../../../.prettierrc`), {encoding: 'utf8'})
);

const prettierFormat = (content: string) => {
    return prettier.format(content, {...config, parser: 'typescript'});
};

const transformer = transform([
    lodashTransform('')
]);

beforeEach(() => {
    cleanupFullImports();
});

describe('webpack lodash transform', () => {
    describe('lodash', () => {
        test('newest ts features', () => {
            const ORIGIN = prettierFormat(`
                import type {XXX} from './types';

                export type {XXX} from './types';

                const x: [a: string] = [''];
            `);

            const EXPECT = prettierFormat(`
                import type {XXX} from './types';

                export type {XXX} from './types';

                const x: [a: string] = [''];
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
        });

        test('replace without default import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {get, flow, set} from 'lodash';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/get';
                import flow from 'lodash/flow';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(0);
        });

        test('replace with default import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _, {get, flow, set} from 'lodash';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _ from 'lodash';

                import get from 'lodash/get';
                import flow from 'lodash/flow';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(1);
        });

        test('replace with multiple import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _, {debounce} from 'lodash';
                import {get, flow, set} from 'lodash';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _ from 'lodash';
                import debounce from 'lodash/debounce';
                import get from 'lodash/get';
                import flow from 'lodash/flow';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(1);
        });

        test('replace with assigned import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {get, isEmpty as _isEmpty, set} from 'lodash';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/get';
                import _isEmpty from 'lodash/isEmpty';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(0);
        });

        test('do not change module imports', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/get';
                import isEmpty from 'lodash/isEmpty';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/get';
                import isEmpty from 'lodash/isEmpty';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(0);
        });
    });

    describe('lodash/fp', () => {
        test('replace without default import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {get, flow, set} from 'lodash/fp';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/fp/get';
                import flow from 'lodash/fp/flow';
                import set from 'lodash/fp/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(0);
        });

        test('replace with default import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _, {get, flow, set} from 'lodash/fp';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _ from 'lodash/fp';

                import get from 'lodash/fp/get';
                import flow from 'lodash/fp/flow';
                import set from 'lodash/fp/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(1);
        });

        test('replace with multiple import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _, {debounce} from 'lodash/fp';
                import {get, flow, set} from 'lodash/fp';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _ from 'lodash/fp';
                import debounce from 'lodash/fp/debounce';
                import get from 'lodash/fp/get';
                import flow from 'lodash/fp/flow';
                import set from 'lodash/fp/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(1);
        });

        test('replace with assigned import', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {get, isEmpty as _isEmpty, set} from 'lodash/fp';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/fp/get';
                import _isEmpty from 'lodash/fp/isEmpty';
                import set from 'lodash/fp/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(0);
        });

        test('do not change module imports', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/fp/get';
                import isEmpty from 'lodash/fp/isEmpty';
                import set from 'lodash/fp/set';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import get from 'lodash/fp/get';
                import isEmpty from 'lodash/fp/isEmpty';
                import set from 'lodash/fp/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(0);
        });
    });

    describe('mixed', () => {
        test('replace', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _, {debounce} from 'lodash/fp';
                import {get, flow as _flow, set} from 'lodash';

                const val = get(this, 'val');
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import _ from 'lodash/fp';
                import debounce from 'lodash/fp/debounce';
                import get from 'lodash/get';
                import _flow from 'lodash/flow';
                import set from 'lodash/set';

                const val = get(this, 'val');
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
            expect(getFullImports().length).toBe(1);
        });
    });

    describe('predicate', () => {
        expect(predicate({
            resourcePath: 'node_modules/lodash',
            content: 'import {get} from \'lodash\';'
        })).toBe(false);

        expect(predicate({
            resourcePath: 'packages/geo/src/bundles/geozones/components/modal/',
            content: 'import {get} from \'lodash\';'
        })).toBe(true);

        expect(predicate({
            resourcePath: 'packages/geo/src/bundles/geozones/components/modal/',
            content: 'import {get} from \'lodash/fp\';'
        })).toBe(true);

        expect(predicate({
            resourcePath: 'packages/geo/src/bundles/geozones/components/modal/',
            content: 'const lodash = {}'
        })).toBe(false);
    });
});

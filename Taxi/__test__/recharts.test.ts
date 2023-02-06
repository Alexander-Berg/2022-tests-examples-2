
import fs from 'fs';
import path from 'path';

import {predicate, transform as rechartsTransform} from '../transforms/recharts';
import transform from '../utils/transform';

// tslint:disable-next-line: no-var-requires
const prettier = require('prettier');

const config = JSON.parse(
    fs.readFileSync(path.resolve(__dirname, `../../../../../../.prettierrc`), {encoding: 'utf8'})
);

const prettierFormat = (content: string) => {
    return prettier.format(content, {...config, parser: 'typescript'});
};

const transformer = transform([
    rechartsTransform()
]);

describe('webpack recharts transform', () => {
    test('replace without assigned import', () => {
        const ORIGIN = prettierFormat(`
            import React from 'react';
            import {Line, Area, Treemap, Pie} from 'recharts';

            const val = <Line />;
        `);

        const EXPECT = prettierFormat(`
            import React from 'react';
            import Line from 'recharts/lib/cartesian/Line';
            import Area from 'recharts/lib/cartesian/Area';
            import Treemap from 'recharts/lib/chart/Treemap';
            import Pie from 'recharts/lib/polar/Pie';

            const val = <Line />;
        `);

        const result = prettierFormat((transformer(ORIGIN)));

        expect(result).toBe(EXPECT);
    });

    test('replace with assigned import', () => {
        const ORIGIN = prettierFormat(`
            import React from 'react';
            import {Line as _Line, Area, Treemap as Mmm, Pie} from 'recharts';

            const val = <Line />;
        `);

        const EXPECT = prettierFormat(`
            import React from 'react';
            import _Line from 'recharts/lib/cartesian/Line';
            import Area from 'recharts/lib/cartesian/Area';
            import Mmm from 'recharts/lib/chart/Treemap';
            import Pie from 'recharts/lib/polar/Pie';

            const val = <Line />;
        `);

        const result = prettierFormat((transformer(ORIGIN)));

        expect(result).toBe(EXPECT);
    });
});

describe('recharts predicate', () => {
    expect(predicate({
        resourcePath: 'node_modules/recharts',
        content: 'import {Line} from \'recharts\';',
    })).toBeFalsy();

    expect(predicate({
        resourcePath: 'packages/geo/src/bundles/geozones/components/modal/',
        content: 'import {Line} from \'recharts\';',
    })).toBeTruthy();

    expect(predicate({
        resourcePath: 'packages/geo/src/bundles/geozones/components/modal/',
        content: 'const recharts = {};',
    })).toBeFalsy();
});

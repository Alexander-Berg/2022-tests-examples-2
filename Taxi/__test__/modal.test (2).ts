import fs from 'fs';
import path from 'path';

import {predicate, transform as modalTransform} from '../transforms/modal';
import transform from '../utils/transform';

// tslint:disable-next-line: no-var-requires
const prettier = require('prettier');

const config = JSON.parse(
    fs.readFileSync(path.resolve(__dirname, `../../../../../../.prettierrc`), {encoding: 'utf8'})
);

const prettierFormat = (content: string) => {
    return prettier.format(content, {...config, parser: 'typescript'});
};

const ALIAS = '_blocks/modal';

const transformer = transform([
    modalTransform(ALIAS)
]);

describe('webpack modal transform', () => {
    describe('amber-blocks/modal', () => {
        test('libs only', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {Modal as BaseModal, ModalContent} from 'amber-blocks/modal';
                import Section from 'amber-blocks/section';

                class ModalRequest extends React.PureComponent {}
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {ModalContent} from 'amber-blocks/modal';
                import Section from 'amber-blocks/section';

                import BaseModal from '_blocks/modal';

                class ModalRequest extends React.PureComponent {}
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
        });

        test('libs and static', () => {
            const ORIGIN = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {Modal, ModalContent} from 'amber-blocks/modal';
                import Section from 'amber-blocks/section';

                import actions from '_infrastructure/actions';

                class ModalRequest extends React.PureComponent {}
            `);

            const EXPECT = prettierFormat(`
                import React from 'react';
                import PropTypes from 'prop-types';
                import {ModalContent} from 'amber-blocks/modal';
                import Section from 'amber-blocks/section';

                import Modal from '_blocks/modal';

                import actions from '_infrastructure/actions';

                class ModalRequest extends React.PureComponent {}
            `);

            const result = prettierFormat(transformer(ORIGIN));

            expect(result).toBe(EXPECT);
        });
    });

    describe('predicate', () => {
        expect(predicate({
            resourcePath: 'packages/core/src/components/blocks/modal/',
            content: 'import {Modal as BaseModal, ModalContent} from \'amber-blocks/modal\';'
        })).toBe(false);

        expect(predicate({
            resourcePath: 'packages/geo/src/bundles/geozones/components/modal/',
            content: 'import {Modal, ModalContent} from \'amber-blocks/modal\';'
        })).toBe(true);
    });
});

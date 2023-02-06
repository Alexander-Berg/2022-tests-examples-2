/* eslint-disable @typescript-eslint/no-explicit-any */
import {range} from 'lodash';
import pMap from 'p-map';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {User} from '@/src/entities/user/entity';
import {TankerAttributeOptionsExporter} from 'service/tanker-attribute-options-exporter';
import TankerProvider from 'service/tanker-provider';
import {AttributeType} from 'types/attribute';

describe('tanker attribute options exporter', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should upload attributes only "select" and "multiselect"', async () => {
        await Promise.all(
            [
                AttributeType.TEXT,
                AttributeType.STRING,
                AttributeType.IMAGE,
                AttributeType.BOOLEAN,
                AttributeType.NUMBER
            ].map(async (type) =>
                TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {type}
                })
            )
        );

        const optionKeys = await pMap(
            [AttributeType.SELECT, AttributeType.MULTISELECT],
            async (type) => {
                const attr = await TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {type}
                });

                const option = await TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: attr.id,
                        sortOrder: 0,
                        nameTranslationMap: {ru: 'ur', fr: 'rf'}
                    }
                });

                return `${attr.code}.${option.code}`;
            },
            {concurrency: 1}
        );

        let keyset: any;
        let keys: any;

        jest.spyOn(TankerProvider.prototype as any, 'upsertKeyset').mockImplementation(async (params: any) => {
            keyset = params.keyset;
            keys = params.keys;
        });

        const tankerAttributeOptionsExporter = new TankerAttributeOptionsExporter();
        await tankerAttributeOptionsExporter.upsertAttributeOptions();

        expect(keyset).toMatch(/^AttributeOptions/);
        expect(keys).toEqual([
            {
                name: optionKeys[0],
                translations: {ru: 'ur', fr: 'rf', en: ''}
            },
            {
                name: optionKeys[1],
                translations: {ru: 'ur', fr: 'rf', en: ''}
            }
        ]);
    });

    it('should read by chunks', async () => {
        await Promise.all(
            range(5).map(async (i) => {
                const attr = await TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {type: i > 3 ? AttributeType.SELECT : AttributeType.MULTISELECT}
                });

                await TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: attr.id,
                        sortOrder: 0,
                        nameTranslationMap: {ru: 'ur', fr: 'rf'}
                    }
                });
            })
        );

        let execCount = 0;

        jest.spyOn(TankerProvider.prototype as any, 'upsertKeyset').mockImplementation(async () => {
            execCount++;
        });

        const tankerAttributeOptionsExporter = new TankerAttributeOptionsExporter();
        await tankerAttributeOptionsExporter.upsertAttributeOptions();

        expect(execCount).toBe(2);
    });
});

import {range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AttributeType} from 'types/attribute';

import type {InfoModel} from './entity';

describe('info model isCompatibleWith method', () => {
    let user: User;
    let region: Region;
    let infoModel: InfoModel;
    let attributes: Attribute[];
    let requiredAttributes: Attribute[];

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        attributes = await Promise.all(
            range(3).map(() =>
                TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {
                        type: AttributeType.NUMBER
                    }
                })
            )
        );
        requiredAttributes = await Promise.all(
            range(3).map(() =>
                TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {
                        type: AttributeType.NUMBER,
                        isValueRequired: true
                    }
                })
            )
        );
        infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {id: attributes[0].id},
                {id: attributes[1].id},
                {id: requiredAttributes[0].id},
                {id: requiredAttributes[1].id}
            ]
        });
    });

    // Инфо модель совместима, если у неё такой же набор атрибутов
    it('should pass info model with same attributes', async () => {
        const otherInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {id: attributes[0].id},
                {id: attributes[1].id},
                {id: requiredAttributes[0].id},
                {id: requiredAttributes[1].id}
            ]
        });

        expect(infoModel.isCompatibleWith(otherInfoModel)).toBeTruthy();
    });

    // Инфо модель совместима, если она включает в себя тот же набор атрибутов, а другие атрибуты необазательны
    it('should pass info model with new optional attributes', async () => {
        const otherInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {id: attributes[0].id},
                {id: attributes[1].id},
                {id: attributes[2].id},
                {id: requiredAttributes[0].id},
                {id: requiredAttributes[1].id}
            ]
        });

        expect(infoModel.isCompatibleWith(otherInfoModel)).toBeTruthy();
    });

    // Инфо модель несовместима, если у неё нет каких-то атрибутов
    it('should not pass info model without some attributes', async () => {
        const otherInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: attributes[0].id}, {id: requiredAttributes[0].id}, {id: requiredAttributes[1].id}]
        });

        expect(infoModel.isCompatibleWith(otherInfoModel)).toBeFalsy();
    });

    // Инфо модель несовместима, если новые атрибуты обязательны
    it('should not pass info model with new required attributes', async () => {
        const otherInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {id: attributes[0].id},
                {id: attributes[1].id},
                {id: requiredAttributes[0].id},
                {id: requiredAttributes[1].id},
                {id: requiredAttributes[2].id}
            ]
        });

        expect(infoModel.isCompatibleWith(otherInfoModel)).toBeFalsy();
    });
});

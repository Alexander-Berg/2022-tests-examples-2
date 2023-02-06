/* eslint-disable @typescript-eslint/no-explicit-any */
import {first_name, last_name, username, uuid} from 'casual';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import type {Connection, EntityManager, EntityTarget, Repository} from 'typeorm';

import {Attribute} from '@/src/entities/attribute/entity';
import {AttributeOption} from '@/src/entities/attribute-option/entity';
import {FrontCategory} from '@/src/entities/front-category/entity';
import {FrontCategoryProduct} from '@/src/entities/front-category-product/entity';
import {InfoModel} from '@/src/entities/info-model/entity';
import {InfoModelAttribute} from '@/src/entities/info-model-attribute/entity';
import {Lang} from '@/src/entities/lang/entity';
import {MasterCategory} from '@/src/entities/master-category/entity';
import {Product} from '@/src/entities/product/entity';
import {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import {Region} from '@/src/entities/region/entity';
import {User} from '@/src/entities/user/entity';
import {toHstoreValue} from '@/src/service/hstore-type/to-hstore-value';
import {ensureConnection, executeInTransaction} from 'service/db';
import {AttributeType} from 'types/attribute';
import type {HistorableEntity} from 'types/common';
import {FrontCategoryStatus} from 'types/front-category';
import {MasterCategoryStatus} from 'types/master-category';
import {ProductStatus} from 'types/product';

import {History} from './entity';

declare global {
    namespace jest {
        interface Matchers<R> {
            toContainValues<EntityRecord>(expected: EntityRecord): R;
            toBelongTo<T>(expected: EntityTarget<T>): R;
        }
    }
}

async function createUser() {
    const connection = await ensureConnection();
    const {manager} = connection.getRepository(User);

    const user = manager.create(User, {
        login: username,
        staffData: {
            name: {
                first: {ru: first_name},
                last: {ru: last_name}
            }
        }
    });

    await manager.save(user);

    return Number(user.id);
}

describe('history triggers', () => {
    let authorId: number;
    let regionId: number;
    let connection: Connection;

    beforeEach(async () => {
        connection = await ensureConnection();
        authorId = await createUser();
        const langRepo = connection.getRepository(Lang);
        await langRepo.save(langRepo.create({isoCode: uuid}));

        const regionRepo = connection.getRepository(Region);
        regionId = Number((await regionRepo.save(langRepo.create({isoCode: uuid}))).id);
    });

    expect.extend({
        toContainValues<T extends HistorableEntity>({tableName, newRow}: History<T>, expected: T) {
            if (!newRow) {
                return {pass: false, message: () => 'Property newRow is not set'};
            }

            for (const column of connection.getMetadata(expected.constructor).nonVirtualColumns) {
                const entityKey = column.propertyName;
                const entityValue = (expected as Record<string, any>)[entityKey];
                const hstoreKey = column.databaseName;
                let hstoreValue = (newRow as Record<string, string | undefined | null>)[hstoreKey];

                if (entityValue === undefined) {
                    continue;
                }
                if (hstoreKey === 'history_subject_id') {
                    continue; // skip history_subject_id as it is not stored
                }
                if (hstoreValue === undefined) {
                    return {
                        pass: false,
                        message: () =>
                            `The key "${hstoreKey}" is not included in\n  ` +
                            `History.newRow: ${JSON.stringify(newRow)}`
                    };
                }
                if (column.type === 'json' || column.type === 'jsonb') {
                    hstoreValue = hstoreValue ? JSON.stringify(JSON.parse(hstoreValue)) : hstoreValue;
                    continue;
                }

                const convertedEntityValue = toHstoreValue(entityValue);
                if (convertedEntityValue !== hstoreValue) {
                    return {
                        pass: false,
                        message: () =>
                            `${tableName}[${entityKey}]: ${hstoreValue} != ${convertedEntityValue}\n` +
                            `History.newRow: ${JSON.stringify(newRow)}\n` +
                            `Entity: ${JSON.stringify(expected)}`
                    };
                }
            }
            return {pass: true, message: () => ''};
        },
        toBelongTo<T>(historyRecord: History, target: EntityTarget<T>) {
            const {metadata} = connection.getRepository(target);
            return {
                pass: historyRecord.tableName === metadata.tableName,
                message: () =>
                    `Table name is expected to be "${metadata.tableName}"\n` +
                    `but history contains "${historyRecord.tableName}"`
            };
        }
    });

    function executeInTransactionInternal<T>(callback: (manager: EntityManager) => Promise<T>) {
        return executeInTransaction({authorId, stamp: MOCKED_STAMP, source: 'ui'}, callback);
    }

    function executeInTransactionWithEntity<T>(
        target: EntityTarget<T>,
        callback: (manager: Repository<T>) => Promise<T>
    ) {
        return executeInTransactionInternal((manager) => callback(manager.getRepository(target)));
    }

    it('should save attribute history', async () => {
        // Insert
        await executeInTransactionWithEntity(Attribute, async (repo) => {
            return repo.save(repo.create({code: uuid, type: AttributeType.TEXT, ticket: 'ticket1'}));
        });
        const attribute = await connection.getRepository(Attribute).findOneOrFail();
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(1);
        expect(historyRows[0].authorId).toBe(authorId);
        expect(historyRows[0]).toBelongTo(Attribute);
        expect(historyRows[0]).toContainValues(attribute);

        // Update
        attribute.ticket = 'ticket2';
        await executeInTransactionInternal((manager) => manager.save(Attribute, attribute));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(2);
        expect(historyRows[1].authorId).toBe(authorId);
        expect(historyRows[1]).toBelongTo(Attribute);
        expect(historyRows[1]).toContainValues(attribute);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(Attribute, {id: attribute.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(3);
        expect(historyRows[2].authorId).toBe(authorId);
        expect(historyRows[2]).toBelongTo(Attribute);

        expect(historyRows[1].newRow).toStrictEqual(historyRows[2].oldRow);
        expect(historyRows[2].newRow).toBeNull();
    });

    it('should save attribute_option history', async () => {
        // Insert
        const attributeOptions = await executeInTransactionInternal(async (manager) => {
            const attribute = await manager.save(
                Attribute,
                manager.create(Attribute, {code: uuid, type: AttributeType.TEXT})
            );
            return manager.save(AttributeOption, [
                manager.create(AttributeOption, {code: uuid, attribute, sortOrder: 0}),
                manager.create(AttributeOption, {code: uuid, attribute, sortOrder: 1})
            ]);
        });
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(3);

        expect(historyRows[1].authorId).toBe(authorId);
        expect(historyRows[2].authorId).toBe(authorId);

        expect(historyRows[1]).toBelongTo(AttributeOption);
        expect(historyRows[2]).toBelongTo(AttributeOption);

        expect(historyRows[1]).toContainValues(attributeOptions[0]);
        expect(historyRows[2]).toContainValues(attributeOptions[1]);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(AttributeOption, {id: attributeOptions[1].id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(4);
        expect(historyRows[3].authorId).toBe(authorId);
        expect(historyRows[3]).toBelongTo(AttributeOption);
        expect(historyRows[2].newRow).toStrictEqual(historyRows[3].oldRow);
        expect(historyRows[3].newRow).toBeNull();
    });

    it('should save info_model history', async () => {
        // Insert
        const im = await executeInTransactionWithEntity(InfoModel, (repo) =>
            repo.save(repo.create({code: uuid, regionId}))
        );
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(1);
        expect(historyRows[0].authorId).toBe(authorId);
        expect(historyRows[0]).toBelongTo(InfoModel);
        expect(historyRows[0]).toContainValues(im);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(InfoModel, {id: im.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(2);
        expect(historyRows[1].authorId).toBe(authorId);
        expect(historyRows[1]).toBelongTo(InfoModel);
        expect(historyRows[0].newRow).toStrictEqual(historyRows[1].oldRow);
        expect(historyRows[1].newRow).toBeNull();
    });

    it('should save info_model_attribute history', async () => {
        // Insert
        await executeInTransactionInternal(async (manager) => {
            const attribute = await manager.save(
                Attribute,
                manager.create(Attribute, {code: uuid, type: AttributeType.TEXT})
            );
            const infoModel = await manager.save(InfoModel, manager.create(InfoModel, {code: uuid, regionId}));
            return manager.save(InfoModelAttribute, manager.create(InfoModelAttribute, {infoModel, attribute}));
        });
        const ima = await connection.getRepository(InfoModelAttribute).findOneOrFail();
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(3);
        expect(historyRows[2].authorId).toBe(authorId);
        expect(historyRows[2]).toBelongTo(InfoModelAttribute);
        expect(historyRows[2]).toContainValues(ima);

        // Update
        ima.isImportant = true;
        await executeInTransactionInternal((manager) => manager.save(InfoModelAttribute, ima));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(4);
        expect(historyRows[3].authorId).toBe(authorId);
        expect(historyRows[3]).toBelongTo(InfoModelAttribute);
        expect(historyRows[3]).toContainValues(ima);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(InfoModelAttribute, {id: ima.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(5);
        expect(historyRows[4].authorId).toBe(authorId);
        expect(historyRows[4]).toBelongTo(InfoModelAttribute);
        expect(historyRows[3].newRow).toStrictEqual(historyRows[4].oldRow);
        expect(historyRows[4].newRow).toBeNull();
    });

    it('should save master_category history', async () => {
        // Insert
        await executeInTransactionInternal(async (manager) => {
            const infoModel = await manager.save(InfoModel, manager.create(InfoModel, {code: uuid, regionId}));
            return manager.save(MasterCategory, manager.create(MasterCategory, {code: uuid, regionId, infoModel}));
        });
        const mc = await connection.getRepository(MasterCategory).findOneOrFail();
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(2);
        expect(historyRows[1].authorId).toBe(authorId);
        expect(historyRows[1]).toBelongTo(MasterCategory);
        expect(historyRows[1]).toContainValues(mc);

        // Update
        mc.status = MasterCategoryStatus.ACTIVE;
        await executeInTransactionInternal((manager) => manager.save(MasterCategory, mc));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(3);
        expect(historyRows[2].authorId).toBe(authorId);
        expect(historyRows[2]).toBelongTo(MasterCategory);
        expect(historyRows[2]).toContainValues(mc);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(MasterCategory, {id: mc.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(4);
        expect(historyRows[3].authorId).toBe(authorId);
        expect(historyRows[3]).toBelongTo(MasterCategory);
        expect(historyRows[2].newRow).toStrictEqual(historyRows[3].oldRow);
        expect(historyRows[3].newRow).toBeNull();
    });

    it('should save front_category history', async () => {
        // Insert
        await executeInTransactionWithEntity(FrontCategory, (repo) =>
            repo.save(repo.create({code: uuid, regionId, imageUrl: '', deeplink: 'some deeplink'}))
        );
        const fc = await connection.getRepository(FrontCategory).findOneOrFail();
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(1);
        expect(historyRows[0].authorId).toBe(authorId);
        expect(historyRows[0]).toBelongTo(FrontCategory);
        expect(historyRows[0]).toContainValues(fc);

        // Update
        fc.status = FrontCategoryStatus.ACTIVE;
        await executeInTransactionInternal((manager) => manager.save(FrontCategory, fc));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(2);
        expect(historyRows[1].authorId).toBe(authorId);
        expect(historyRows[1]).toBelongTo(FrontCategory);
        expect(historyRows[1]).toContainValues(fc);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(FrontCategory, {id: fc.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(3);
        expect(historyRows[2].authorId).toBe(authorId);
        expect(historyRows[2]).toBelongTo(FrontCategory);
        expect(historyRows[1].newRow).toStrictEqual(historyRows[2].oldRow);
        expect(historyRows[2].newRow).toBeNull();
    });

    it('should save front_category_product history', async () => {
        // Insert
        const fcp = await executeInTransactionInternal(async (manager) => {
            const infoModel = await manager.save(InfoModel, manager.create(InfoModel, {code: uuid, regionId}));
            const masterCategory = await manager.save(
                MasterCategory,
                manager.create(MasterCategory, {code: uuid, regionId, infoModel})
            );
            const frontCategory = await manager.save(
                FrontCategory,
                manager.create(FrontCategory, {code: uuid, regionId, imageUrl: ''})
            );
            const product = await manager.save(
                Product,
                manager.create(Product, {code: uuid, regionId, masterCategory})
            );
            return manager.save(FrontCategoryProduct, manager.create(FrontCategoryProduct, {product, frontCategory}));
        });
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(5); // im, mc, fc, p, fcp
        expect(historyRows[4].authorId).toBe(authorId);
        expect(historyRows[4]).toBelongTo(FrontCategoryProduct);
        expect(historyRows[4]).toContainValues(fcp);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(FrontCategoryProduct, {id: fcp.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(6);
        expect(historyRows[5].authorId).toBe(authorId);
        expect(historyRows[5]).toBelongTo(FrontCategoryProduct);
        expect(historyRows[4].newRow).toStrictEqual(historyRows[5].oldRow);
        expect(historyRows[5].newRow).toBeNull();
    });

    it('should save product history', async () => {
        // Insert
        await executeInTransactionInternal(async (manager) => {
            const infoModel = await manager.save(InfoModel, manager.create(InfoModel, {code: uuid, regionId}));
            const masterCategory = await manager.save(
                MasterCategory,
                manager.create(MasterCategory, {code: uuid, regionId, infoModel})
            );
            return manager.save(Product, manager.create(Product, {code: uuid, regionId, masterCategory}));
        });
        const product = await connection.getRepository(Product).findOneOrFail();
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(3);
        expect(historyRows[2].authorId).toBe(authorId);
        expect(historyRows[2]).toBelongTo(Product);
        expect(historyRows[2]).toContainValues(product);

        // Update
        product.status = ProductStatus.ACTIVE;
        await executeInTransactionInternal((manager) => manager.save(Product, product));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(4);
        expect(historyRows[3].authorId).toBe(authorId);
        expect(historyRows[3]).toBelongTo(Product);
        expect(historyRows[3]).toContainValues(product);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(Product, {id: product.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(5);
        expect(historyRows[4].authorId).toBe(authorId);
        expect(historyRows[4]).toBelongTo(Product);
        expect(historyRows[3].newRow).toStrictEqual(historyRows[4].oldRow);
        expect(historyRows[4].newRow).toBeNull();
    });

    it('should save product_attribute_value history', async () => {
        // Insert
        const pav = await executeInTransactionInternal(async (manager) => {
            const infoModel = await manager.save(InfoModel, manager.create(InfoModel, {code: uuid, regionId}));
            const masterCategory = await manager.save(
                MasterCategory,
                manager.create(MasterCategory, {code: uuid, regionId, infoModel})
            );
            const product = await manager.save(
                Product,
                manager.create(Product, {code: uuid, regionId, masterCategory})
            );
            const attribute = await manager.save(
                Attribute,
                manager.create(Attribute, {code: uuid, type: AttributeType.TEXT})
            );
            return manager.save(
                ProductAttributeValue,
                // NOTE: array or jsonb are not decently supported by the toContainValues matcher
                manager.create(ProductAttributeValue, {product, attribute, value: uuid})
            );
        });
        let historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(5);
        expect(historyRows[4].authorId).toBe(authorId);
        expect(historyRows[4]).toBelongTo(ProductAttributeValue);
        expect(historyRows[4]).toContainValues(pav);

        // Delete
        await executeInTransactionInternal((manager) => manager.delete(ProductAttributeValue, {id: pav.id}));
        historyRows = await connection.getRepository(History).find({order: {id: 'ASC'}});

        expect(historyRows).toHaveLength(6);
        expect(historyRows[5].authorId).toBe(authorId);
        expect(historyRows[5]).toBelongTo(ProductAttributeValue);
        expect(historyRows[4].newRow).toStrictEqual(historyRows[5].oldRow);
        expect(historyRows[5].newRow).toBeNull();
    });
});

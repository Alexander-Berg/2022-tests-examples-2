import assert from 'assert';
import {uuid} from 'casual';
import {chunk, maxBy, range} from 'lodash';
import pMap from 'p-map';
import type {EntityManager} from 'typeorm';
import {IsNull} from 'typeorm';

import {IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER} from '@/src/constants/import';
import {Attribute} from '@/src/entities/attribute/entity';
import {ImportImage} from '@/src/entities/import-image/entity';
import {ImportSpreadsheet} from '@/src/entities/import-spreadsheet/entity';
import {InfoModel} from '@/src/entities/info-model/entity';
import {InfoModelAttribute} from '@/src/entities/info-model-attribute/entity';
import {MasterCategory} from '@/src/entities/master-category/entity';
import {Product} from '@/src/entities/product/entity';
import {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import {Region} from '@/src/entities/region/entity';
import {User} from '@/src/entities/user/entity';
import {ensureConnection, executeInTransaction, setDeferrableDeferred, setTransactionScope} from 'service/db';
import {CommitHandler} from 'service/import/commit-handler';
import {AttributeType} from 'types/attribute';
import {ProductStatus} from 'types/product';

type AsyncReadinessInterface<T = void> = {
    ready: Promise<T>;
};

type ImportTesterOptions = {
    userLogin: string;
    regionIsoCode: string;
    attributesCount: number;
    chunkSize?: number;
    concurrency?: number;
};

type CommonAttribute = {
    id: number;
    type: string;
    code: string;
};

let _uniqueInteger = 0;
const uniqueInteger = () => ++_uniqueInteger;

export class ImportTester implements AsyncReadinessInterface {
    protected importKey: string;
    protected userLogin: string;
    protected regionIsoCode: string;
    protected attributesCount: number;
    protected chunkSize: number;
    protected concurrency: number;
    protected initStamp = uuid;

    protected user: User;
    protected region: Region;
    protected requiredAttributes: Attribute[];
    protected commonAttributes: CommonAttribute[] = [];
    protected imageAttribute: Attribute;
    protected infoModel: InfoModel;
    protected masterCategory: MasterCategory;
    protected attributeMap: Map<number, Attribute> = new Map();

    public readonly ready: Promise<void>;

    /**
     * master_category | identifier | image | ...requiredAttributes | ...commonAttributes
     */
    protected entries: string[][] = [];
    protected products: Map<number, Product> = new Map();

    public constructor({
        userLogin,
        regionIsoCode,
        attributesCount,
        chunkSize = 100,
        concurrency = 3
    }: ImportTesterOptions) {
        this.importKey = uuid;
        this.userLogin = userLogin;
        this.regionIsoCode = regionIsoCode;
        this.attributesCount = attributesCount;
        this.chunkSize = chunkSize;
        this.concurrency = concurrency;

        const init = async () => {
            const connection = await ensureConnection();
            await connection.transaction(async (manager) => {
                this.user = await this.loadUser(manager);
                this.region = await this.loadRegion(manager);
                this.requiredAttributes = await this.loadRequiredAttributes(manager);

                await setTransactionScope(manager, {authorId: this.user.id, source: 'import', stamp: this.initStamp});

                this.commonAttributes = await this.createAttributes(manager);
                this.imageAttribute = await this.createImageAttribute(manager);
                this.infoModel = await this.createInfoModel(manager);
                this.masterCategory = await this.createMasterCategory(manager);

                this.infoModel.attributes.forEach((attribute) => this.attributeMap.set(attribute.id, attribute));
            });
        };

        this.ready = init();
    }

    public getInitStamp() {
        return this.initStamp;
    }

    public getUser() {
        return this.user;
    }

    public async generateInsertEntries({count}: {count: number}) {
        await this.handleChunked(count, async (chunk) => {
            for (let i = 0; i < chunk.length; i++) {
                const {imageUrl} = await this.createImage();
                const entry: string[] = [
                    this.masterCategory.code,
                    '',
                    imageUrl,
                    ...this.getAttributeCellValue(
                        [...this.requiredAttributes, ...this.commonAttributes].map(({id}) => id)
                    )
                ];
                this.entries.push(entry);
            }
        });
    }

    public async generateUpdateEntries({count}: {count: number}) {
        await this.handleChunked(count, async (chunk) => {
            await executeInTransaction({authorId: this.user.id, source: 'import', stamp: uuid}, async (manager) => {
                await setDeferrableDeferred(manager);
                for (let i = 0; i < chunk.length; i++) {
                    const product = await this.createProduct(manager);

                    const cellValues = await this.getAttributeCellValueForUpdate(
                        manager,
                        product.id,
                        [...this.requiredAttributes, ...this.commonAttributes].map(({id}) => id)
                    );

                    const {imageUrl} = await this.createImage();

                    const entry: string[] = ['', product.identifier + '', imageUrl, ...cellValues];
                    this.entries.push(entry);
                }
            });
        });
    }

    public countInfoModelAttributes() {
        return this.infoModel.attributes.length;
    }

    public async dispatchEntries() {
        const header: string[] = [
            MASTER_CATEGORY_HEADER,
            IDENTIFIER_HEADER,
            this.imageAttribute.code,
            ...this.getAttributeCellHeader([...this.requiredAttributes, ...this.commonAttributes].map(({id}) => id))
        ];

        const connection = await ensureConnection();
        const {manager} = connection.getRepository(ImportSpreadsheet);
        return manager.save(
            manager.create(ImportSpreadsheet, {
                importKey: this.importKey,
                regionId: this.region.id,
                content: [header, ...this.entries]
            })
        );
    }

    public async commit() {
        const commitHandler = new CommitHandler({importKey: this.importKey, authorId: this.user.id});
        const result = await commitHandler.handle();
        assert(typeof result === 'undefined', 'Broken import commit!');
    }

    protected loadUser(manager: EntityManager) {
        return manager.getRepository(User).findOneOrFail({where: {login: this.userLogin}});
    }

    protected loadRegion(manager: EntityManager) {
        return manager.getRepository(Region).findOneOrFail({
            where: {isoCode: this.regionIsoCode},
            relations: ['langs']
        });
    }

    protected loadRequiredAttributes(manager: EntityManager) {
        return manager.getRepository(Attribute).find({where: {isValueRequired: true}});
    }

    protected async createAttributes(manager: EntityManager) {
        const result = await manager
            .createQueryBuilder()
            .insert()
            .into(Attribute)
            .values([...Array(this.attributesCount)].map(() => ({code: uuid, type: AttributeType.STRING})))
            .returning(['id', 'type', 'code'])
            .execute();

        return result.raw as CommonAttribute[];
    }

    protected async createImageAttribute(manager: EntityManager) {
        const attribute = manager.create(Attribute, {code: uuid, type: AttributeType.IMAGE});

        await manager.save(attribute);

        return manager.findOneOrFail(Attribute, attribute.id);
    }

    protected async createInfoModel(manager: EntityManager) {
        const infoModel = manager.create(InfoModel, {code: uuid, regionId: this.region.id});

        await manager.save(infoModel);

        await manager.getRepository(InfoModelAttribute).insert(
            [{id: this.imageAttribute.id}, ...this.requiredAttributes, ...this.commonAttributes].map(({id}, i) => ({
                sortOrder: i,
                infoModelId: infoModel.id,
                attributeId: id
            }))
        );

        return manager.findOneOrFail(InfoModel, infoModel.id, {relations: ['attributes']});
    }

    protected async createMasterCategory(manager: EntityManager) {
        const root = await manager
            .getRepository(MasterCategory)
            .findOneOrFail({where: {parentId: IsNull(), regionId: this.region.id}});

        const children = await manager.getRepository(MasterCategory).find({parentId: root.id});
        const lastSortOrder = maxBy(children, (it) => it.sortOrder)?.sortOrder ?? -1;

        const masterCategory = manager.create(MasterCategory, {
            code: uuid,
            infoModelId: this.infoModel.id,
            regionId: this.region.id,
            parentId: root.id,
            sortOrder: lastSortOrder + 1
        });

        await manager.save(masterCategory);

        return manager.findOneOrFail(MasterCategory, masterCategory.id, {relations: ['infoModelMasterCategoryCache']});
    }

    protected async createImage() {
        const connection = await ensureConnection();
        const {manager} = connection.getRepository(ImportImage);
        const imageKey = uuid;
        return manager.save(
            manager.create(ImportImage, {
                importKey: this.importKey,
                relPath: imageKey,
                imageUrl: imageKey,
                regionId: this.region.id
            })
        );
    }

    protected async createProduct(manager: EntityManager) {
        const {id} = await manager.save(
            manager.create(Product, {
                masterCategoryId: this.masterCategory.id,
                regionId: this.region.id,
                status: ProductStatus.ACTIVE,
                code: uuid
            })
        );
        const product = await manager.getRepository(Product).findOneOrFail(id);
        this.products.set(product.id, product);

        return product;
    }

    protected getAttributeCellHeader(attributeIds: number[]) {
        const out: string[] = [];

        for (const attributeId of attributeIds) {
            const attribute = this.attributeMap.get(attributeId);
            assert(attribute, `Missed attribute map key: "${attributeId}"`);

            if (attribute.type === AttributeType.STRING && attribute.isValueLocalizable) {
                out.push(...this.region.langs.map(({isoCode}) => [attribute.code, isoCode].join('|')));
            } else {
                out.push(attribute.code);
            }
        }

        return out;
    }

    protected getAttributeCellValue(attributeIds: number[]) {
        const out: string[] = [];

        for (const attributeId of attributeIds) {
            const attribute = this.attributeMap.get(attributeId);
            assert(attribute, `Missed attribute map key: "${attributeId}"`);

            if (attribute.type === AttributeType.STRING) {
                out.push(...(attribute.isValueLocalizable ? this.region.langs.map(() => uuid) : [uuid]));
            } else if (attribute.type === AttributeType.NUMBER) {
                out.push('' + uniqueInteger());
            } else {
                throw new Error(`Unhandled attribute type: "${attribute.type}"`);
            }
        }

        return out;
    }

    protected async getAttributeCellValueForUpdate(manager: EntityManager, productId: number, attributeIds: number[]) {
        const out: string[] = [];

        const values: Pick<ProductAttributeValue, 'productId' | 'attributeId' | 'value' | 'langId'>[] = [];
        attributeIds.forEach((attributeId) => {
            const attribute = this.attributeMap.get(attributeId);
            assert(attribute, `Missed attribute map key: "${attributeId}"`);

            const prevValues = this.getAttributeCellValue([attributeId]);
            if (attribute.isValueLocalizable) {
                this.region.langs.forEach(({id}, i) => {
                    values.push({productId, attributeId, langId: id, value: prevValues[i]});
                });
            } else {
                values.push({productId, attributeId, langId: null, value: prevValues[0]});
            }

            const nextValues = this.getAttributeCellValue([attributeId]);
            out.push(...nextValues);
        });

        await manager.createQueryBuilder().insert().into(ProductAttributeValue).values(values).execute();

        return out;
    }

    protected async handleChunked(count: number, handler: (part: number[]) => Promise<void>) {
        await pMap(chunk(range(0, count), this.chunkSize), handler, {concurrency: this.concurrency});
    }
}

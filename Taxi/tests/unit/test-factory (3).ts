/* eslint-disable @typescript-eslint/no-explicit-any */
import type {Staff} from '@lavka-js-toolbox/staff-provider';
import camelcaseKeys from 'camelcase-keys';
import {first_name, integer, last_name, seed, username, uuid, word, words} from 'casual';
import {chain, keyBy, maxBy, pick, range} from 'lodash';
import {FindConditions, In} from 'typeorm';
import type {QueryDeepPartialEntity} from 'typeorm/query-builder/QueryPartialEntity';

import {Attribute} from '@/src/entities/attribute/entity';
import {AttributeGroup} from '@/src/entities/attribute-group/entity';
import {AttributeOption} from '@/src/entities/attribute-option/entity';
import {Category} from '@/src/entities/catalog/category/entity';
import {CategoryFrontCategory} from '@/src/entities/catalog/category-front-category/entity';
import {CategoryImage} from '@/src/entities/catalog/category-image/entity';
import {Grid} from '@/src/entities/catalog/grid/entity';
import {GridGroup} from '@/src/entities/catalog/grid-group/entity';
import {GridGroupImage} from '@/src/entities/catalog/grid-group-image/entity';
import {Group} from '@/src/entities/catalog/group/entity';
import {GroupCategory} from '@/src/entities/catalog/group-category/entity';
import {GroupCategoryImage} from '@/src/entities/catalog/group-category-image/entity';
import {GroupImage} from '@/src/entities/catalog/group-image/entity';
import {getImageDimension} from '@/src/entities/catalog/image-dimension/api/get-image-dimension';
import {DbTable} from '@/src/entities/const';
import {FrontCategory} from '@/src/entities/front-category/entity';
import {FrontCategoryProduct} from '@/src/entities/front-category-product/entity';
import {History} from '@/src/entities/history/entity';
import {HistorySubject} from '@/src/entities/history-subject/entity';
import {ImageCache} from '@/src/entities/image-cache/entity';
import {ImportImage} from '@/src/entities/import-image/entity';
import {ImportSpreadsheet} from '@/src/entities/import-spreadsheet/entity';
import {InfoModel} from '@/src/entities/info-model/entity';
import {InfoModelAttribute} from '@/src/entities/info-model-attribute/entity';
import {InfoModelFullness} from '@/src/entities/info-model-fullness/entity';
import {Lang} from '@/src/entities/lang/entity';
import {Locale} from '@/src/entities/locale/entity';
import {MasterCategory} from '@/src/entities/master-category/entity';
import {MasterCategoryFullness} from '@/src/entities/master-category-fullness/entity';
import {MasterCategoryFullnessQueue} from '@/src/entities/master-category-fullness-queue/entity';
import {Product} from '@/src/entities/product/entity';
import {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import {ProductCombo} from '@/src/entities/product-combo/entity';
import {ProductComboGroup} from '@/src/entities/product-combo-group/entity';
import {ProductComboOption} from '@/src/entities/product-combo-option/entity';
import {ProductComboProduct} from '@/src/entities/product-combo-product/entity';
import {ProductConfirmation} from '@/src/entities/product-confirmation/entity';
import {ProductFullness} from '@/src/entities/product-fullness/entity';
import {ProductFullnessQueue} from '@/src/entities/product-fullness-queue/entity';
import {Region} from '@/src/entities/region/entity';
import {Role} from '@/src/entities/role/entity';
import {TaskQueue} from '@/src/entities/task-queue/entity';
import {User} from '@/src/entities/user/entity';
import {UserProductFilter} from '@/src/entities/user-product-filter/entity';
import {UserRole} from '@/src/entities/user-role/entity';
import type {UILanguage} from '@/src/i18n';
import {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {ensureConnection, executeInTransaction, HistorySource, setDeferrableImmediate} from '@/src/service/db';
import {FrontCategoryStatus} from '@/src/types/front-category';
import type {RawRow} from 'service/import/spreadsheet';
import {ProductProvider} from 'service/product-provider';
import type {AttributeType} from 'types/attribute';
import type {LocalizedConfirmationValue} from 'types/attribute-confirmation';
import type {LocalizedValue, MultipleLocalizedValue} from 'types/attribute-value';
import {CatalogStatus} from 'types/catalog/base';
import type {DbImageMeta} from 'types/image';
import {ImportMode} from 'types/import';
import {MasterCategoryStatus} from 'types/master-category';
import type {ProductAttribute, ProductStatus} from 'types/product';
import {ProductComboStatus, ProductComboType} from 'types/product-combo';
import type {Rules} from 'types/role';
import type {TranslationMap} from 'types/translation';

seed(3);

async function getManager() {
    const connection = await ensureConnection();
    return connection.createQueryRunner().manager;
}

async function dispatchDeferred() {
    const manager = await TestFactory.getManager();
    return setDeferrableImmediate(manager);
}

async function dispatchHistory(...fields: (keyof History)[]) {
    await dispatchDeferred();
    const history = await TestFactory.getHistory();
    return fields?.length ? history.map((it) => pick(it, ...fields)) : history;
}

interface CreateUserParams {
    staffData?: Partial<Staff.Person>;
    rules?: Rules;
}

async function createUser({staffData, rules}: CreateUserParams = {}) {
    const connection = await ensureConnection();
    const {manager} = connection.getRepository(User);

    const user = manager.create(User, {
        login: username,
        staffData:
            staffData ||
            ({
                name: {
                    first: {
                        ru: first_name
                    },
                    last: {
                        ru: last_name
                    }
                }
            } as any)
    });

    await manager.save(user);

    if (rules) {
        const role = await createRole(rules);
        await createUserRole({userId: user.id, roleId: role.id});
    }

    return manager.findOneOrFail(User, user.id);
}

async function getUsers() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(User);

    return repository.createQueryBuilder().getMany();
}

async function getHistory() {
    const connection = await ensureConnection();
    return connection.getRepository(History).find();
}

async function flushHistory() {
    const connection = await ensureConnection();
    return connection.createQueryBuilder().delete().from(History).execute();
}

async function callBuildCategoriesCacheFunction() {
    const connection = await ensureConnection();
    const buildCacheResult = await connection.query('select * from build_categories_history_cache();');

    return camelcaseKeys(buildCacheResult);
}

async function callBuildProductCacheFunction() {
    const connection = await ensureConnection();
    const buildCacheResult = await connection.query('select * from build_product_history_cache();');

    return camelcaseKeys(buildCacheResult);
}

interface ParsedHistoryElement {
    id: number;
    table: string;
    action: 'D' | 'I' | 'U';
    old: {
        id: number;
        code: string;
        identifier: number;
        front_category_id: number;
    };
    new: {
        id: number;
        code: string;
        front_category_id: number;
    };
}

async function getParsedHistory(): Promise<ParsedHistoryElement[]> {
    const connection = await ensureConnection();

    return connection.query(
        // eslint-disable-next-line max-len
        `
            select hstore_to_json(history.new_row) as new,
            hstore_to_json(history.old_row) as old,
            id, action, table_name as table
            from history
        `
    );
}

interface CreateRegionParams {
    code?: string;
}

async function createRegion(params: CreateRegionParams = {}) {
    const connection = await ensureConnection();

    const {manager} = connection.getRepository(Region);

    const region = manager.create(Region, {
        isoCode: (params.code || uuid).toUpperCase()
    });

    await manager.save(region);

    return manager.findOneOrFail(Region, region.id);
}

async function createLang({isoCode = uuid}: {isoCode?: string} = {}) {
    const connection = await ensureConnection();

    const {manager} = connection.getRepository(Lang);

    const lang = manager.create(Lang, {isoCode});

    await manager.save(lang);

    return manager.findOneOrFail(Lang, lang.id);
}

interface CreateLocaleParams {
    regionId: number;
    langIds: number[];
}

async function createLocale(params: CreateLocaleParams) {
    const connection = await ensureConnection();

    const {manager} = connection.getRepository(Lang);

    await Promise.all(
        params.langIds.map(async (langId) => {
            const loc = manager.create(Locale, {
                regionId: params.regionId,
                langId
            });

            await manager.save(loc);
        })
    );
}

type CreateLangDictParams = {count: number};

async function createLangDict(params: CreateLangDictParams) {
    const langPromises = range(params.count).map(() => createLang());

    return keyBy(await Promise.all(langPromises), ({isoCode}) => isoCode);
}

interface CreateApiContextParams {
    params?: any;
    query?: any;
    body?: any;
    user?: User;
    region?: Region;
    lang?: Lang;
}

interface TestApiRequestContextParams extends CreateApiContextParams {
    user: User;
    region: Region;
    lang: Lang;
}

class TestApiRequestContext extends ApiRequestContext {
    params: TestApiRequestContextParams;

    constructor(params: TestApiRequestContextParams) {
        super({} as any);
        this.params = params;
    }

    getParams = () => this.params.params;
    getQuery = () => this.params.query;
    getBody = () => this.params.body;
    getUser = async () => this.params.user;
    getAuthLogin = () => this.params.user.login;
    getRegion = async () => this.params.region;
    getRegionCode = () => this.params.region.isoCode;
    getLang = async () => this.params.lang;
    getRegionLangs = async () => [this.params.lang];
    getDefaultRegionLang = async () => this.params.lang;
    getLangCode = () => this.params.lang.isoCode as UILanguage;
    getStamp = () => MOCKED_STAMP;
}

async function createApiContext(params: CreateApiContextParams = {}) {
    return new TestApiRequestContext({
        ...params,
        user: params.user ?? (await createUser()),
        lang: params.lang ?? (await createLang()),
        region: params.region ?? (await createRegion())
    });
}

async function getAttributes() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(Attribute);

    return repository.createQueryBuilder().getMany();
}

async function getProducts() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(Product);

    return repository.find({relations: ['historySubject']});
}

async function getAttributeOptions(attributeId: number) {
    const connection = await ensureConnection();
    const repository = connection.getRepository(AttributeOption);

    return repository.find({where: {attributeId}, order: {sortOrder: 'ASC'}});
}

interface CreateAttributeParams {
    attribute: DeepPartial<Attribute>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function createAttribute({
    attribute: {
        code,
        type,
        isValueLocalizable,
        isValueRequired,
        isUnique,
        isImmutable,
        isArray,
        nameTranslationMap,
        descriptionTranslationMap,
        properties,
        attributeGroupId,
        attributeGroupSortOrder,
        isConfirmable
    },
    userId,
    stamp = MOCKED_STAMP,
    source = 'import'
}: CreateAttributeParams) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const attribute = manager.create(Attribute, {
            code: code || uuid,
            type,
            isValueLocalizable,
            isValueRequired,
            isArray,
            isUnique,
            isImmutable,
            nameTranslationMap,
            descriptionTranslationMap,
            properties,
            attributeGroupId,
            attributeGroupSortOrder,
            isConfirmable
        });

        await manager.save(attribute);

        return manager.findOneOrFail(Attribute, attribute.id);
    });
}

async function createAttributes({
    count,
    authorId,
    type,
    stamp = MOCKED_STAMP,
    source = 'import'
}: {
    count: number;
    authorId: number;
    type: AttributeType;
    stamp?: string;
    source?: HistorySource;
}) {
    return executeInTransaction({authorId, stamp, source}, async (manager) => {
        return manager
            .createQueryBuilder()
            .insert()
            .into(Attribute)
            .values([...Array(count)].map(() => ({code: uuid, type})))
            .returning(['id', 'code'])
            .execute();
    });
}

interface CreateAttributeOptionParams {
    attributeOption: DeepPartial<AttributeOption> & Pick<AttributeOption, 'attributeId'>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function createAttributeOption(params: CreateAttributeOptionParams) {
    const {attributeOption: attributeOptionData, userId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        let sortOrder = attributeOptionData.sortOrder;

        if (!sortOrder) {
            const lastAttributeOption = await manager.findOne(AttributeOption, {
                where: {attributeId: attributeOptionData.attributeId},
                order: {sortOrder: 'DESC'}
            });

            sortOrder = (lastAttributeOption?.sortOrder ?? -1) + 1;
        }

        const attributeOption = manager.create(AttributeOption, {
            attributeId: attributeOptionData.attributeId,
            code: attributeOptionData.code ?? uuid,
            nameTranslationMap: attributeOptionData.nameTranslationMap,
            sortOrder
        });

        await manager.save(attributeOption);

        return manager.findOneOrFail(AttributeOption, attributeOption.id);
    });
}

interface UpdateAttributeParams {
    attribute: DeepPartial<Attribute>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function updateAttribute(attributeId: number, params: UpdateAttributeParams) {
    const {attribute: attributeData, userId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager.getRepository(Attribute).update(attributeId, attributeData as QueryDeepPartialEntity<Attribute>);
    });
}

interface UpdateInfoModelParams {
    infoModel: DeepPartial<InfoModel>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function updateInfoModel(infoModelId: number, params: UpdateInfoModelParams) {
    const {infoModel: infoModelData, userId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager.getRepository(InfoModel).update(infoModelId, {
            ...(infoModelData.titleTranslationMap ? {titleTranslationMap: infoModelData.titleTranslationMap} : {}),
            ...(infoModelData.descriptionTranslationMap
                ? {descriptionTranslationMap: infoModelData.descriptionTranslationMap}
                : {})
        });
    });
}

interface UpdateFrontCategoryParams {
    frontCategory: DeepPartial<FrontCategory>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function updateFrontCategory(frontCategoryId: number, params: UpdateFrontCategoryParams) {
    const {userId, frontCategory, stamp = MOCKED_STAMP, source = 'ui'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager.getRepository(FrontCategory).update(frontCategoryId, {
            ...(frontCategory.deeplink ? {deeplink: frontCategory.deeplink} : {}),
            ...(frontCategory.parentId ? {parentId: frontCategory.parentId} : {})
        });
    });
}

interface UpdateMasterCategoryParams {
    masterCategory: DeepPartial<MasterCategory>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function updateMasterCategory(masterCategoryId: number, params: UpdateMasterCategoryParams) {
    const {userId, masterCategory, stamp = MOCKED_STAMP, source = 'ui'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager.getRepository(MasterCategory).update(masterCategoryId, {
            ...(masterCategory.status ? {status: masterCategory.status} : {}),
            ...(masterCategory.parentId ? {parentId: masterCategory.parentId} : {})
        });
    });
}

interface UpdateProductParams {
    product: DeepPartial<Product>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function updateProduct(productId: number, params: UpdateProductParams) {
    const {userId, product, stamp = MOCKED_STAMP, source = 'ui'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager.getRepository(Product).update(productId, {
            ...(product.status ? {status: product.status} : {}),
            ...(product.masterCategoryId ? {masterCategoryId: product.masterCategoryId} : {})
        });
    });
}

async function getInfoModelAttributes() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(InfoModelAttribute);

    return repository.createQueryBuilder('imAttr').leftJoinAndSelect('imAttr.attribute', 'attr').getMany();
}

async function getMasterCategories() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(MasterCategory);

    return repository.createQueryBuilder().getMany();
}

async function getFrontCategories() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(FrontCategory);

    return repository.createQueryBuilder().getMany();
}

interface CreateProductAttributeValueParams {
    userId: number;
    productId: number;
    attributeId: number;
    value: any;
    langId?: number;
    stamp?: string;
    source?: HistorySource;
    isConfirmed?: boolean;
}

async function createProductAttributeValue(params: CreateProductAttributeValueParams) {
    const {
        userId,
        value,
        langId,
        productId,
        attributeId,
        stamp = MOCKED_STAMP,
        source = 'import',
        isConfirmed = false
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const productAttributeValue = manager.create(ProductAttributeValue, {
            value,
            productId,
            attributeId,
            isConfirmed,
            ...(langId ? {langId} : {})
        });

        await manager.save(productAttributeValue);

        return manager.findOneOrFail(ProductAttributeValue, productAttributeValue.id);
    });
}

async function updateProductAttributeValue({
    userId,
    productId,
    attributeId,
    volume,
    stamp = MOCKED_STAMP,
    source = 'import'
}: {
    userId: number;
    productId: number;
    attributeId: number;
    volume: QueryDeepPartialEntity<ProductAttributeValue>;
    stamp?: string;
    source?: HistorySource;
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager
            .getRepository(ProductAttributeValue)
            .createQueryBuilder()
            .update()
            .set(volume)
            .where('product_id = :productId AND attribute_id = :attributeId', {productId, attributeId})
            .returning('id')
            .execute();
    });
}

async function deleteProductAttributeValue({
    userId,
    productId,
    attributeId,
    stamp = MOCKED_STAMP,
    source = 'import'
}: {
    userId: number;
    productId: number;
    attributeId: number;
    stamp?: string;
    source?: HistorySource;
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager
            .getRepository(ProductAttributeValue)
            .createQueryBuilder()
            .delete()
            .where('product_id = :productId AND attribute_id = :attributeId', {productId, attributeId})
            .execute();
    });
}

export interface LocalizableValue {
    langId: number;
    value: string | string[];
}

interface CreateLocalizedProductAttributeValue {
    userId: number;
    productId: number;
    attributeId: number;
    values: LocalizableValue[];
}

async function createLocalizedProductAttributeValue(params: CreateLocalizedProductAttributeValue) {
    const {userId, values, attributeId, productId} = params;

    return Promise.all(
        values.map(async (it) =>
            TestFactory.createProductAttributeValue({
                userId,
                productId,
                attributeId,
                value: it.value,
                langId: it.langId
            })
        )
    );
}

export interface AttributeShort {
    id: number;
    isImportant?: boolean;
}

interface CreateInfoModelParams {
    regionId: number;
    userId: number;
    attributes?: AttributeShort[];
    infoModel?: DeepPartial<InfoModel>;
    stamp?: string;
    source?: HistorySource;
}

async function createInfoModel(params: CreateInfoModelParams) {
    const {attributes, regionId, userId, infoModel: infoModelData, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const infoModel = manager.create(InfoModel, {
            code: infoModelData?.code || uuid,
            regionId,
            titleTranslationMap: infoModelData?.titleTranslationMap,
            descriptionTranslationMap: infoModelData?.descriptionTranslationMap
        });

        await manager.save(infoModel);

        await TestFactory.linkAttributesToInfoModel({
            userId,
            infoModelId: infoModel.id,
            attributes: attributes || []
        });

        return manager.findOneOrFail(InfoModel, infoModel.id, {relations: ['attributes']});
    });
}

interface LinkAttributesToInfoModelParams {
    userId: number;
    attributes: AttributeShort[];
    infoModelId: number;
    stamp?: string;
    source?: HistorySource;
}

async function linkAttributesToInfoModel(params: LinkAttributesToInfoModelParams) {
    const {userId, attributes, infoModelId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        await manager.getRepository(InfoModelAttribute).insert(
            attributes.map(({id, isImportant}) => ({
                infoModelId,
                attributeId: id,
                isImportant
            }))
        );
    });
}

interface UnlinkAttributesFromInfoModelParams {
    userId: number;
    attributes: AttributeShort[];
    infoModelId: number;
    stamp?: string;
    source?: HistorySource;
}

async function unlinkAttributesFromInfoModel(params: UnlinkAttributesFromInfoModelParams) {
    const {userId, attributes, infoModelId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        await manager
            .createQueryBuilder()
            .delete()
            .from(InfoModelAttribute)
            .where('attributeId IN (:...attributeIds)', {attributeIds: attributes.map(({id}) => id)})
            .andWhere('infoModelId = :infoModelId', {infoModelId})
            .execute();
    });
}

interface CreateMasterCategoryParams {
    infoModelId?: number;
    userId: number;
    regionId: number;
    nameTranslationMap?: TranslationMap;
    descriptionTranslationMap?: TranslationMap;
    parentId?: number;
    sortOrder?: number;
    status?: MasterCategoryStatus;
    akeneoLegacy?: boolean;
    code?: string;
    stamp?: string;
    source?: HistorySource;
}

async function createMasterCategory(params: CreateMasterCategoryParams) {
    const {
        infoModelId,
        userId,
        regionId,
        parentId,
        nameTranslationMap,
        akeneoLegacy,
        descriptionTranslationMap,
        status = MasterCategoryStatus.ACTIVE,
        code = uuid,
        stamp = MOCKED_STAMP,
        source = 'import'
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        let sortOrder = params.sortOrder;

        if (sortOrder === undefined && parentId !== undefined) {
            const children = await manager.getRepository(MasterCategory).find({parentId});
            const lastSortOrder = maxBy(children, (it) => it.sortOrder)?.sortOrder ?? -1;

            sortOrder = lastSortOrder + 1;
        }

        const masterCategory = manager.create(MasterCategory, {
            code,
            infoModelId,
            parentId,
            regionId,
            sortOrder,
            akeneoLegacy,
            status,
            nameTranslationMap,
            descriptionTranslationMap
        });

        await manager.save(masterCategory);

        return manager.findOneOrFail(MasterCategory, masterCategory.id, {relations: ['infoModelMasterCategoryCache']});
    });
}

interface DeleteParams {
    userId: number;
    id: number;
    stamp?: string;
    source?: HistorySource;
}

async function deleteMasterCategory(params: DeleteParams) {
    const {stamp = MOCKED_STAMP, source = 'import'} = params;
    return executeInTransaction({authorId: params.userId, stamp, source}, async (manager) => {
        return manager.createQueryBuilder().delete().from(MasterCategory).where('id = :id', {id: params.id}).execute();
    });
}

async function deleteFrontCategory(params: DeleteParams) {
    const {stamp = MOCKED_STAMP, source = 'import'} = params;
    return executeInTransaction({authorId: params.userId, stamp, source}, async (manager) => {
        await manager
            .createQueryBuilder()
            .delete()
            .from(FrontCategoryProduct)
            .where('frontCategoryId = :id', {id: params.id})
            .execute();

        return manager.createQueryBuilder().delete().from(FrontCategory).where('id = :id', {id: params.id}).execute();
    });
}

async function deleteProduct(params: DeleteParams) {
    const {stamp = MOCKED_STAMP, source = 'import'} = params;
    return executeInTransaction({authorId: params.userId, stamp, source}, async (manager) => {
        return manager.createQueryBuilder().delete().from(Product).where('id = :id', {id: params.id}).execute();
    });
}

interface CreateProductParams {
    masterCategoryId: number;
    userId: number;
    regionId: number;
    code?: string;
    identifier?: number;
    status?: ProductStatus;
    stamp?: string;
    source?: HistorySource;
    isMeta?: boolean;
}

async function createProduct(params: CreateProductParams) {
    const {
        userId,
        masterCategoryId,
        regionId,
        status,
        code,
        identifier,
        stamp = MOCKED_STAMP,
        source = 'import',
        isMeta = false
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const product = manager.create(Product, {masterCategoryId, regionId, status, code, identifier, isMeta});

        await manager.save(product);

        return manager.findOneOrFail(Product, product.id);
    });
}

interface CreateFrontCategoryProductParams {
    userId: number;
    productId: number;
    frontCategoryId: number;
    stamp?: string;
    source?: HistorySource;
}

async function createFrontCategoryProduct(params: CreateFrontCategoryProductParams) {
    const {userId, productId, frontCategoryId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const frontCategoryProduct = manager.create(FrontCategoryProduct, {
            productId,
            frontCategoryId
        });

        await manager.save(frontCategoryProduct);

        return manager.findOneOrFail(FrontCategoryProduct, frontCategoryProduct.id);
    });
}

interface CreateFrontCategoryParams extends Partial<FrontCategory> {
    userId: number;
    productIds?: number[];
    stamp?: string;
    source?: HistorySource;
}

async function createFrontCategory(params: CreateFrontCategoryParams) {
    const {
        code,
        parentId,
        productIds,
        userId,
        regionId,
        akeneoLegacy,
        nameTranslationMap,
        descriptionTranslationMap,
        sortOrder,
        status,
        deeplink,
        timetable,
        legalRestrictions,
        promo,
        stamp = MOCKED_STAMP,
        source = 'import'
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        let order = sortOrder;

        if (order === undefined && parentId) {
            const children = await manager.getRepository(FrontCategory).find({where: {parentId}});
            const lastSortOrder = maxBy(children, (it) => it.sortOrder)?.sortOrder ?? -1;
            const firstPosition = lastSortOrder === -1 ? 0 : lastSortOrder;

            order = firstPosition + 1;
        }

        const frontCategory = manager.create(FrontCategory, {
            code: code ?? uuid,
            regionId,
            parentId,
            imageUrl: word,
            deeplink: deeplink || word + integer(10_000_000, 99_999_999),
            sortOrder: order,
            akeneoLegacy,
            status: status ?? FrontCategoryStatus.ACTIVE,
            legalRestrictions: legalRestrictions ?? word,
            promo,
            nameTranslationMap,
            descriptionTranslationMap,
            timetable
        });

        await manager.save(frontCategory);

        await TestFactory.linkProductsToFrontCategory({
            userId,
            productIds: productIds || [],
            frontCategoryId: frontCategory.id
        });

        return manager.findOneOrFail(FrontCategory, frontCategory.id);
    });
}

async function createNestedFrontCategory({
    authorId,
    regionId,
    depth
}: {
    authorId: number;
    regionId: number;
    depth: number;
}) {
    const out: FrontCategory[] = [];

    let parentId: undefined | number = undefined;
    for (let k = 0; k < depth; k++) {
        const frontCategory: FrontCategory = await TestFactory.createFrontCategory({
            userId: authorId,
            regionId,
            parentId
        });
        out.push(frontCategory);
        parentId = frontCategory.id;
    }

    return {scope: out, last: out[out.length - 1]};
}

interface LinkProductsToFrontCategoryParams {
    userId: number;
    productIds: number[];
    frontCategoryId: number;
    stamp?: string;
    source?: HistorySource;
}

async function linkProductsToFrontCategory(params: LinkProductsToFrontCategoryParams) {
    const {userId, productIds, frontCategoryId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        await manager.getRepository(FrontCategoryProduct).insert(
            productIds.map((productId) => ({
                productId,
                frontCategoryId
            }))
        );
    });
}

interface UnlinkProductsFromFrontCategoryParams {
    userId: number;
    productIds: number[];
    frontCategoryId: number;
    stamp?: string;
    source?: HistorySource;
}

async function unlinkProductsFromFrontCategory(params: UnlinkProductsFromFrontCategoryParams) {
    const {userId, productIds, frontCategoryId, stamp = MOCKED_STAMP, source = 'import'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        await manager
            .createQueryBuilder()
            .delete()
            .from(FrontCategoryProduct)
            .where('productId IN (:...productIds)')
            .andWhere('frontCategoryId = :frontCategoryId')
            .setParameters({
                productIds,
                frontCategoryId
            })
            .execute();
    });
}

interface CreateTranslationMapParams {
    langCodes: string[];
    values?: string[];
}

function createTranslationMap(params: CreateTranslationMapParams) {
    const {values, langCodes} = params;

    const translationMap: TranslationMap = {};

    langCodes.forEach((langCode, i) => {
        translationMap[langCode] = (values || [])[i] || uuid;
    });

    return translationMap;
}

async function createImportSpreadsheet({
    importKey = uuid,
    regionId,
    content,
    mode = ImportMode.NORMAL
}: {
    importKey?: string;
    regionId?: number;
    content: RawRow[];
    mode?: ImportMode;
}) {
    if (!regionId) {
        const region = await createRegion();
        regionId = region.id;
    }

    const connection = await ensureConnection();
    const {manager} = connection.getRepository(ImportSpreadsheet);
    return manager.save(manager.create(ImportSpreadsheet, {importKey, regionId, content, mode}));
}

async function createImportImage({
    importKey = uuid,
    relPath = uuid,
    imageUrl,
    regionId,
    error
}: {
    importKey?: string;
    relPath?: string;
    imageUrl?: string;
    regionId: number;
    error?: string;
}) {
    const connection = await ensureConnection();
    const {manager} = connection.getRepository(ImportImage);
    return manager.save(manager.create(ImportImage, {importKey, relPath, imageUrl, regionId, error}));
}

async function createImageCache({
    md5 = uuid,
    url,
    meta = {
        name: 'test.jpg',
        size: 100000,
        width: 900,
        height: 900
    }
}: {
    md5?: string;
    url: string;
    meta?: DbImageMeta;
}) {
    const connection = await ensureConnection();
    const {manager} = connection.getRepository(ImageCache);
    return manager.save(manager.create(ImageCache, {md5, url, meta}));
}

async function createUserProductFilter({
    userId,
    regionId,
    name,
    query
}: {
    userId: number;
    regionId: number;
    name?: string;
    query?: string;
}) {
    const connection = await ensureConnection();
    const {manager} = connection.getRepository(UserProductFilter);

    const filter = manager.create(UserProductFilter, {
        regionId,
        userId,
        name: name || words(3),
        query: query || words(5)
    });

    await manager.save(filter);

    return manager.findOneOrFail(UserProductFilter, filter.id);
}

async function getProductAttributeValues({productId}: {productId: number}) {
    const connection = await ensureConnection();
    return connection.getRepository(ProductAttributeValue).find({where: {productId}});
}

async function getFrontCategoryProduct(params: {productId: number} | {frontCategoryId: number}) {
    const connection = await ensureConnection();
    return connection.getRepository(FrontCategoryProduct).find({where: params, relations: ['frontCategory']});
}

async function getHistorySubject(id: number) {
    const connection = await ensureConnection();
    return connection.getRepository(HistorySubject).findOneOrFail({where: {id}});
}

async function createProductFullness({productId, fullness = 100}: {productId: number; fullness?: number}) {
    const {manager} = await ensureConnection();
    return manager.save(manager.create(ProductFullness, {productId, fullness}));
}

async function createMasterCategoryFullness({
    masterCategoryId,
    fullness = 100
}: {
    masterCategoryId: number;
    fullness?: number;
}) {
    const {manager} = await ensureConnection();
    return manager.save(manager.create(MasterCategoryFullness, {masterCategoryId, fullness}));
}

async function getProductFullness(productId: number) {
    const connection = await ensureConnection();
    return connection.getRepository(ProductFullness).findOneOrFail({where: {productId}});
}

async function getProductsFullness(productIds: number[]) {
    const connection = await ensureConnection();
    return connection.getRepository(ProductFullness).find({productId: In(productIds)});
}

async function getMasterCategoryFullness(masterCategoryId: number) {
    const connection = await ensureConnection();
    return connection.getRepository(MasterCategoryFullness).findOneOrFail({where: {masterCategoryId}});
}

async function getInfoModelFullness(infoModelId: number) {
    const connection = await ensureConnection();
    return connection.getRepository(InfoModelFullness).findOneOrFail({where: {infoModelId}});
}

async function getMasterCategoriesFullness(masterCategoryIds: number[]) {
    const connection = await ensureConnection();
    return connection.getRepository(MasterCategoryFullness).find({masterCategoryId: In(masterCategoryIds)});
}

async function getProductConfirmation(productId: number) {
    const connection = await ensureConnection();
    return connection.getRepository(ProductConfirmation).findOneOrFail({where: {productId}});
}

async function getTaskQueue() {
    const connection = await ensureConnection();
    return connection.getRepository(TaskQueue).find();
}

async function getFormattedTaskQueue() {
    const connection = await ensureConnection();
    const tasks = await connection.getRepository(TaskQueue).find();

    return tasks.map((task) => ({info: task.info}));
}

async function getProductFullnessQueue() {
    const connection = await ensureConnection();
    return connection.getRepository(ProductFullnessQueue).find();
}

async function getMasterCategoryFullnessQueue() {
    const connection = await ensureConnection();
    return connection.getRepository(MasterCategoryFullnessQueue).find();
}

async function getUserProductFilters() {
    const connection = await ensureConnection();
    return connection.getRepository(UserProductFilter).find();
}

interface UpdateProductViaUiParams {
    user: User;
    role: Role;
    region: Region;
    stamp?: string;
    productData: {
        changeStatus?: (oldStatus: ProductStatus) => ProductStatus;
        changeMasterCategory?: (oldMasterCategoryId: number) => number;
        changeFrontCategories?: (oldFrontCategoryIds: number[]) => number[];
        changeAttributes?: (oldAttributes: ProductAttribute[]) => ProductAttribute[];
    };
}
async function updateProductViaUi(product: Product, params: UpdateProductViaUiParams) {
    const {user, role, stamp = MOCKED_STAMP, region, productData} = params;
    const identity = <T>(arg: T) => arg;

    const {
        changeStatus = identity,
        changeMasterCategory = identity,
        changeFrontCategories = identity,
        changeAttributes = identity
    } = productData;

    const manager = await TestFactory.getManager();
    const fcp = await manager.find(FrontCategoryProduct, {where: {product}});
    const pav = await manager.find(ProductAttributeValue, {where: {product}, relations: ['lang', 'attribute']});
    const oldAttributes = chain(pav)
        .groupBy(({attributeId}) => attributeId)
        .values()
        .map((items) => {
            const [item] = items;
            return {
                attributeId: item.attributeId,
                value: item.attribute.isValueLocalizable
                    ? items.reduce(
                          (acc, it) => ({...acc, [it.lang.isoCode]: it.value}),
                          {} as LocalizedValue | MultipleLocalizedValue
                      )
                    : item.value,
                isConfirmed: item.attribute.isValueLocalizable
                    ? items.reduce(
                          (acc, it) => ({...acc, [it.lang.isoCode]: it.isConfirmed}),
                          {} as LocalizedConfirmationValue
                      )
                    : item.isConfirmed
            };
        })
        .value();

    await new ProductProvider({
        user,
        rules: role.rules,
        region,
        stamp,
        identifier: product.identifier,
        productData: {
            status: changeStatus(product.status),
            masterCategoryId: changeMasterCategory(product.masterCategoryId),
            frontCategoryIds: changeFrontCategories(fcp.map(({frontCategoryId}) => frontCategoryId)),
            attributes: changeAttributes(oldAttributes)
        }
    }).update();
}

async function createHistory({
    authorId,
    history
}: {
    authorId: number;
    history: {
        tableName: DbTable;
        action: 'I' | 'U' | 'D';
        oldRow?: Record<string, unknown>;
        newRow?: Record<string, unknown>;
        stamp?: string;
        source?: HistorySource;
        historySubjectId?: number;
    };
}) {
    const manager = await TestFactory.getManager();

    const historySubject = history.historySubjectId
        ? await manager.findOneOrFail(HistorySubject, history.historySubjectId)
        : await manager.save(manager.create(HistorySubject, {authorId, modifierId: authorId}));

    const historyRecord = manager.create(History, {
        authorId,
        action: history.action,
        tableName: history.tableName,
        stamp: history.stamp ?? uuid,
        source: history.source ?? 'manual',
        historySubjectId: historySubject.id,
        oldRow: history.oldRow,
        newRow: history.newRow
    });

    return manager.save(historyRecord);
}

async function getGrids() {
    const connection = await ensureConnection();
    return connection.getRepository(Grid).find();
}

async function getGridGroups(gridId: number) {
    const connection = await ensureConnection();
    return connection
        .getRepository(GridGroup)
        .createQueryBuilder('gridGroup')
        .leftJoinAndSelect('gridGroup.groupImages', 'groupImage')
        .leftJoinAndSelect('groupImage.imageDimension', 'imageDimension')
        .orderBy({
            'gridGroup.sortOrder': 'ASC',
            'groupImage.imageUrl': 'ASC',
            'imageDimension.width': 'ASC',
            'imageDimension.height': 'ASC'
        })
        .where('gridGroup.gridId = :gridId', {gridId})
        .getMany();
}

async function getGroups() {
    const connection = await ensureConnection();
    return connection.getRepository(Group).find();
}

async function getGroupImages(groupId: number) {
    const connection = await ensureConnection();
    return connection.getRepository(GroupImage).find({where: {groupId}, relations: ['imageDimension']});
}

async function getGroupCategories(groupId: number) {
    const connection = await ensureConnection();
    return connection
        .getRepository(GroupCategory)
        .createQueryBuilder('groupCategory')
        .leftJoinAndSelect('groupCategory.categoryImages', 'categoryImage')
        .leftJoinAndSelect('categoryImage.imageDimension', 'imageDimension')
        .orderBy({
            'groupCategory.sortOrder': 'ASC',
            'categoryImage.imageUrl': 'ASC',
            'imageDimension.width': 'ASC',
            'imageDimension.height': 'ASC'
        })
        .where('groupCategory.groupId = :groupId', {groupId})
        .getMany();
}

async function getCategories() {
    const connection = await ensureConnection();
    return connection.getRepository(Category).find();
}

async function getCategoryImages(categoryId: number) {
    const connection = await ensureConnection();
    return connection.getRepository(CategoryImage).find({where: {categoryId}, relations: ['imageDimension']});
}

async function getCategoryFrontCategories(categoryId: number) {
    const connection = await ensureConnection();
    return connection
        .getRepository(CategoryFrontCategory)
        .createQueryBuilder('categoryFrontCategory')
        .orderBy({'categoryFrontCategory.sortOrder': 'ASC'})
        .where('categoryFrontCategory.categoryId = :categoryId', {categoryId})
        .getMany();
}

async function getInfoModels(): Promise<InfoModel[]>;
async function getInfoModels(codes: string): Promise<InfoModel>;
async function getInfoModels(codes: string[]): Promise<InfoModel[]>;
async function getInfoModels(codes?: string | string[]) {
    const connection = await ensureConnection();
    const repository = connection.getRepository(InfoModel);

    if (codes && Array.isArray(codes)) {
        return repository.find({where: {code: codes}});
    }
    if (typeof codes === 'string') {
        return repository.findOneOrFail({where: {code: codes}});
    }
    return repository.find();
}

interface CreateGridParams {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    code?: string;
    regionId: number;
    status?: CatalogStatus;
    shortTitleTranslationMap?: TranslationMap;
    longTitleTranslationMap?: TranslationMap;
    description?: string;
    meta?: Record<string, unknown>;
}

async function createGrid(params: CreateGridParams) {
    const {
        userId,
        stamp = MOCKED_STAMP,
        source = 'ui',
        code = uuid,
        regionId,
        status = CatalogStatus.ACTIVE,
        shortTitleTranslationMap,
        longTitleTranslationMap,
        description,
        meta
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const grid = manager.create(Grid, {
            legacyId: uuid,
            code,
            regionId,
            status,
            shortTitleTranslationMap,
            longTitleTranslationMap,
            description,
            meta
        });

        await manager.save(grid);

        return manager.findOneOrFail(Grid, grid.id);
    });
}
interface CatalogImageParams {
    imageUrl: string;
    filename: string;
    width: number;
    height: number;
}

interface CreateGroupParams {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    code?: string;
    regionId: number;
    status?: CatalogStatus;
    shortTitleTranslationMap?: TranslationMap;
    longTitleTranslationMap?: TranslationMap;
    description?: string;
    meta?: Record<string, unknown>;
    images?: CatalogImageParams[];
}

async function createGroup(params: CreateGroupParams) {
    const {
        userId,
        stamp = MOCKED_STAMP,
        source = 'ui',
        code = uuid,
        regionId,
        status = CatalogStatus.ACTIVE,
        shortTitleTranslationMap,
        longTitleTranslationMap,
        description,
        meta,
        images
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const group = manager.create(Group, {
            legacyId: uuid,
            code,
            regionId,
            status,
            shortTitleTranslationMap,
            longTitleTranslationMap,
            description,
            meta
        });

        await manager.save(group);

        if (images) {
            for (const {imageUrl, filename, width, height} of images) {
                const {id: imageDimensionId} = await getImageDimension({width, height});

                await manager.save(GroupImage, {
                    groupId: group.id,
                    imageUrl,
                    filename,
                    imageDimensionId
                });
            }
        }

        return manager.findOneOrFail(Group, group.id);
    });
}

interface LinkGroupToGridParams {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    gridId: number;
    groupId: number;
    meta?: Record<string, unknown>;
    images?: Omit<CatalogImageParams, 'filename'>[];
}

async function linkGroupToGrid(params: LinkGroupToGridParams) {
    const {userId, stamp = MOCKED_STAMP, source = 'ui', gridId, groupId, meta, images} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const gridGroups = await manager.find(GridGroup, {where: {gridId}});
        const lastSortOrder = maxBy(gridGroups, (it) => it.sortOrder)?.sortOrder ?? -1;
        const gridGroup = await manager.save(GridGroup, {
            gridId,
            groupId,
            sortOrder: lastSortOrder + 1,
            meta
        });

        if (images) {
            for (const {imageUrl, width, height} of images) {
                const {id: imageDimensionId} = await getImageDimension({width, height});
                const groupImage = await manager.findOneOrFail(GroupImage, {imageUrl, imageDimensionId});

                await manager.save(GridGroupImage, {
                    gridGroupId: gridGroup.id,
                    groupImageId: groupImage.id
                });
            }
        }
    });
}

interface CreateCategoryParams {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    code?: string;
    regionId: number;
    status?: CatalogStatus;
    shortTitleTranslationMap?: TranslationMap;
    longTitleTranslationMap?: TranslationMap;
    description?: string;
    meta?: Record<string, unknown>;
    specialCategory?: string;
    deeplink?: string;
    images?: CatalogImageParams[];
}

async function createCategory(params: CreateCategoryParams) {
    const {
        userId,
        stamp = MOCKED_STAMP,
        source = 'ui',
        code = uuid,
        regionId,
        status = CatalogStatus.ACTIVE,
        shortTitleTranslationMap,
        longTitleTranslationMap,
        description,
        meta,
        specialCategory,
        deeplink,
        images
    } = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const category = manager.create(Category, {
            legacyId: uuid,
            code,
            regionId,
            status,
            shortTitleTranslationMap,
            longTitleTranslationMap,
            description,
            meta,
            specialCategory,
            deeplink
        });

        await manager.save(category);

        if (images) {
            for (const {imageUrl, filename, width, height} of images) {
                const {id: imageDimensionId} = await getImageDimension({width, height});

                await manager.save(CategoryImage, {
                    categoryId: category.id,
                    imageUrl,
                    filename,
                    imageDimensionId
                });
            }
        }

        return manager.findOneOrFail(Category, category.id);
    });
}

interface LinkCategoryToGroupParams {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    groupId: number;
    categoryId: number;
    meta?: Record<string, unknown>;
    images?: Omit<CatalogImageParams, 'filename'>[];
}

async function linkCategoryToGroup(params: LinkCategoryToGroupParams) {
    const {userId, stamp = MOCKED_STAMP, source = 'ui', groupId, categoryId, meta, images} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const groupCategories = await manager.find(GroupCategory, {where: {groupId}});
        const lastSortOrder = maxBy(groupCategories, (it) => it.sortOrder)?.sortOrder ?? -1;
        const groupCategory = await manager.save(GroupCategory, {
            groupId,
            categoryId,
            sortOrder: lastSortOrder + 1,
            meta
        });

        if (images) {
            for (const {imageUrl, width, height} of images) {
                const {id: imageDimensionId} = await getImageDimension({width, height});
                const categoryImage = await manager.findOneOrFail(CategoryImage, {imageUrl, imageDimensionId});

                await manager.save(GroupCategoryImage, {
                    groupCategoryId: groupCategory.id,
                    categoryImageId: categoryImage.id
                });
            }
        }
    });
}

interface LinkFrontCategoryToCategoryParams {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    categoryId: number;
    frontCategoryId: number;
}

async function linkFrontCategoryToCategory(params: LinkFrontCategoryToCategoryParams) {
    const {userId, stamp = MOCKED_STAMP, source = 'ui', categoryId, frontCategoryId} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const categoryFrontCategories = await manager.find(CategoryFrontCategory, {where: {categoryId}});
        const lastSortOrder = maxBy(categoryFrontCategories, (it) => it.sortOrder)?.sortOrder ?? -1;

        await manager.save(CategoryFrontCategory, {
            categoryId,
            frontCategoryId,
            sortOrder: lastSortOrder + 1
        });
    });
}

async function createProductCombo({
    userId,
    regionId,
    stamp = MOCKED_STAMP,
    source = 'ui',
    productCombo,
    metaProductsIds
}: {
    userId: number;
    regionId: number;
    stamp?: string;
    source?: HistorySource;
    metaProductsIds?: number[];
    productCombo?: {
        code?: string;
        status?: ProductComboStatus;
        type?: ProductComboType;
        nameTranslationMap?: TranslationMap;
        descriptionTranslationMap?: TranslationMap;
        groups?: {
            nameTranslationMap?: TranslationMap;
            optionsToSelect: number;
            isSelectUnique: boolean;
            options: {productId: number}[];
        }[];
    };
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const {
            status = ProductComboStatus.DISABLED,
            type = ProductComboType.DISCOUNT,
            nameTranslationMap = {},
            descriptionTranslationMap = {},
            groups
        } = productCombo ?? {};

        const entity = manager.create(ProductCombo, {
            status,
            type,
            regionId,
            nameTranslationMap,
            descriptionTranslationMap
        });

        await manager.save(entity);

        if (groups) {
            const productComboGroups: ProductComboGroup[] = [];

            for (const group of groups) {
                const productComboGroup = await TestFactory.createProductComboGroup({
                    userId,
                    source,
                    stamp,
                    productComboGroup: {
                        productComboId: entity.id,
                        nameTranslationMap: group.nameTranslationMap ?? {},
                        optionsToSelect: group.optionsToSelect,
                        isSelectUnique: group.isSelectUnique
                    }
                });
                productComboGroups.push(productComboGroup);
            }

            let index = 0;
            for (const productComboGroup of productComboGroups) {
                const options = groups[index].options;
                for (const option of options) {
                    await TestFactory.createProductComboOption({
                        userId,
                        stamp,
                        source,
                        productComboOption: {
                            productId: option.productId,
                            productComboGroupId: productComboGroup.id
                        }
                    });
                }
                index++;
            }
        }

        if (metaProductsIds) {
            await TestFactory.linkProductsToProductCombo({
                userId,
                stamp,
                source,
                productCombo: entity,
                productComboProductIds: metaProductsIds
            });
        }

        return manager.findOneOrFail(ProductCombo, entity.id, {
            relations: ['groups', 'groups.options', 'products', 'productComboProducts']
        });
    });
}

async function linkProductsToProductCombo({
    userId,
    stamp = MOCKED_STAMP,
    source = 'ui',
    productCombo,
    productComboProductIds
}: {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    productCombo: ProductCombo;
    productComboProductIds: number[];
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const existingEntities = await manager.find(ProductComboProduct, {where: {productCombo}});
        const sortOrder = maxBy(existingEntities, ({sortOrder}) => sortOrder)?.sortOrder ?? -1;

        const entities = productComboProductIds.map((productId, index) =>
            manager.create(ProductComboProduct, {
                productComboId: productCombo.id,
                productId,
                sortOrder: sortOrder + index + 1
            })
        );

        await manager.save(entities);

        return entities;
    });
}

async function getProductCombos(): Promise<ProductCombo[]>;
async function getProductCombos(id: number): Promise<ProductCombo>;
async function getProductCombos(options: FindConditions<ProductCombo>): Promise<ProductCombo[]>;
async function getProductCombos(options?: number | FindConditions<ProductCombo>) {
    const connection = await ensureConnection();
    const repository = connection.getRepository(ProductCombo);
    if (typeof options === 'undefined') {
        return repository.find();
    }
    if (typeof options === 'number') {
        return repository.findOneOrFail(options);
    }

    return repository.find({where: options});
}

async function createProductComboGroup({
    userId,
    stamp = MOCKED_STAMP,
    source = 'ui',
    productComboGroup
}: {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    productComboGroup: {
        productComboId: number;
        nameTranslationMap?: TranslationMap;
        optionsToSelect?: number;
        isSelectUnique?: boolean;
        sortOrder?: number;
    };
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const {productComboId, optionsToSelect = 1, isSelectUnique = true, nameTranslationMap = {}} = productComboGroup;
        let sortOrder = productComboGroup.sortOrder;

        if (!sortOrder) {
            const productComboGroups = await manager.find(ProductComboGroup, {where: {productComboId}});
            const lastSortOrder = maxBy(productComboGroups, {sortOrder})?.sortOrder ?? -1;
            sortOrder = lastSortOrder + 1;
        }

        const entity = manager.create(ProductComboGroup, {
            productComboId,
            nameTranslationMap,
            optionsToSelect,
            isSelectUnique,
            sortOrder
        });

        await manager.save(entity);

        return manager.findOneOrFail(ProductComboGroup, entity.id);
    });
}

async function createProductComboOption({
    userId,
    stamp = MOCKED_STAMP,
    source = 'ui',
    productComboOption
}: {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    productComboOption: {
        productId: number;
        productComboGroupId: number;
        sortOrder?: number;
    };
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const {productId, productComboGroupId} = productComboOption;
        let sortOrder = productComboOption.sortOrder;

        if (!sortOrder) {
            const productComboOptions = await manager.find(ProductComboOption, {where: {productComboGroupId}});
            const lastSortOrder = maxBy(productComboOptions, {sortOrder})?.sortOrder ?? -1;
            sortOrder = lastSortOrder + 1;
        }

        const entity = manager.create(ProductComboOption, {
            productId,
            productComboGroupId,
            sortOrder
        });

        await manager.save(entity);

        return manager.findOneOrFail(ProductComboOption, entity.id);
    });
}

async function deleteProductCombo(params: DeleteParams) {
    const {stamp = MOCKED_STAMP, source = 'ui'} = params;

    return executeInTransaction({authorId: params.userId, stamp, source}, async (manager) => {
        await manager
            .createQueryBuilder()
            .delete()
            .from(ProductComboProduct)
            .where('productComboId = :id', {id: params.id})
            .execute();

        await manager
            .createQueryBuilder()
            .delete()
            .from(ProductComboOption)
            .where((qb) => {
                const subquery = qb
                    .select('pcg.id', 'id')
                    .from(ProductComboGroup, 'pcg')
                    .where('productComboId = :id')
                    .getQuery();

                return `productComboGroupId IN (${subquery})`;
            })
            .setParameters({id: params.id})
            .execute();

        await manager
            .createQueryBuilder()
            .delete()
            .from(ProductComboGroup)
            .where('productComboId = :id', {id: params.id})
            .execute();

        await manager.createQueryBuilder().delete().from(ProductCombo).where('id = :id', {id: params.id}).execute();
    });
}

async function getAttributeGroups() {
    const connection = await ensureConnection();
    const repository = connection.getRepository(AttributeGroup);

    return repository.find();
}
async function getAttributeGroupById(id: number) {
    const connection = await ensureConnection();
    const repository = connection.getRepository(AttributeGroup);

    return repository.findOne({where: {id}, relations: ['attributes']});
}
async function getAttributesByGroupId(groupId: number) {
    const connection = await ensureConnection();
    const repository = connection.getRepository(Attribute);

    return repository.find({where: {attributeGroupId: groupId}, order: {attributeGroupSortOrder: 'ASC'}});
}

async function createAttributeGroup({
    userId,
    stamp = MOCKED_STAMP,
    source = 'ui',
    attributeGroup: {code, nameTranslationMap, descriptionTranslationMap, attributes}
}: {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    attributeGroup: {
        code: string;
        nameTranslationMap?: TranslationMap;
        descriptionTranslationMap?: TranslationMap;
        attributes?: number[];
    };
}) {
    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        const sortOrder =
            (
                await manager
                    .createQueryBuilder(DbTable.ATTRIBUTE_GROUP, 'ag')
                    .select('MAX(ag.sort_order)', 'max')
                    .getRawOne<{max: number}>()
            )?.max ?? -1;

        const entity = manager.create(AttributeGroup, {
            code,
            nameTranslationMap,
            descriptionTranslationMap,
            sortOrder: sortOrder + 1
        });

        await manager.save(entity);

        if (attributes) {
            await TestFactory.linkAttributesToGroup({userId, stamp, source, attributes, groupId: entity.id});
        }

        return await manager.findOneOrFail(AttributeGroup, entity.id, {relations: ['attributes']});
    });
}

async function linkAttributesToGroup({
    userId,
    stamp = MOCKED_STAMP,
    source = 'ui',
    attributes,
    groupId
}: {
    userId: number;
    stamp?: string;
    source?: HistorySource;
    groupId: number;
    attributes: number[];
}) {
    return executeInTransaction({authorId: userId, source, stamp}, (manager) => {
        return manager.getRepository(Attribute).save(
            attributes.map((id, i) => ({
                id,
                attributeGroupId: groupId,
                attributeGroupSortOrder: i
            }))
        );
    });
}

interface UpdateAttributeGroupParams {
    attributeGroup: DeepPartial<AttributeGroup>;
    userId: number;
    stamp?: string;
    source?: HistorySource;
}

async function updateAttributeGroup(attributeGroupId: number, params: UpdateAttributeGroupParams) {
    const {attributeGroup: attributeGroupData, userId, stamp = MOCKED_STAMP, source = 'ui'} = params;

    return executeInTransaction({authorId: userId, stamp, source}, async (manager) => {
        return manager.getRepository(AttributeGroup).update(attributeGroupId, {
            ...(attributeGroupData.nameTranslationMap
                ? {nameTranslationMap: attributeGroupData.nameTranslationMap}
                : {}),
            ...(attributeGroupData.descriptionTranslationMap
                ? {descriptionTranslationMap: attributeGroupData.descriptionTranslationMap}
                : {})
        });
    });
}

async function createRole(rules?: Rules) {
    const connection = await ensureConnection();

    const {manager} = connection.getRepository(Role);

    const role = manager.create(Role, {
        code: uuid,
        nameTranslationMap: {},
        helpTranslationMap: {},
        rules: rules ?? {}
    });

    await manager.save(role);

    return manager.findOneOrFail(Role, role.id);
}

async function getRoles() {
    const connection = await ensureConnection();

    const {manager} = connection.getRepository(Role);

    return manager.find(Role);
}

async function createUserRole({userId, roleId, regionId}: {userId: number; roleId: number; regionId?: number}) {
    const connection = await ensureConnection();

    const {manager} = connection.getRepository(UserRole);

    const userRole = manager.create(UserRole, {
        userId,
        roleId,
        regionId
    });

    await manager.save(userRole);

    return manager.findOneOrFail(UserRole, userRole.id);
}

async function getUserRole(userId: number) {
    const connection = await ensureConnection();

    return connection.getRepository(UserRole).findOne({userId}, {relations: ['user', 'role']});
}

async function getUserRoles(userId: number) {
    const connection = await ensureConnection();

    return connection.getRepository(UserRole).find({where: {userId}, relations: ['user', 'role']});
}

export const TestFactory = {
    getUsers,
    getProducts,
    getHistorySubject,
    getAttributes,
    getAttributeOptions,
    getParsedHistory,
    getInfoModels,
    getInfoModelAttributes,
    getHistory,
    getManager,
    getMasterCategories,
    getFrontCategories,
    getProductAttributeValues,
    getFrontCategoryProduct,
    getProductFullness,
    getProductsFullness,
    getMasterCategoryFullness,
    getMasterCategoriesFullness,
    getInfoModelFullness,
    getTaskQueue,
    getFormattedTaskQueue,
    getProductFullnessQueue,
    getMasterCategoryFullnessQueue,
    getUserProductFilters,
    createUser,
    createAttribute,
    createAttributes,
    createAttributeOption,
    updateAttribute,
    updateInfoModel,
    updateFrontCategory,
    updateMasterCategory,
    updateProduct,
    updateProductAttributeValue,
    deleteProductAttributeValue,
    createInfoModel,
    createMasterCategory,
    createProduct,
    createUserProductFilter,
    createFrontCategory,
    createNestedFrontCategory,
    createFrontCategoryProduct,
    createProductAttributeValue,
    createLocalizedProductAttributeValue,
    createRegion,
    createLang,
    createLocale,
    createLangDict,
    createApiContext,
    createProductFullness,
    createTranslationMap,
    linkAttributesToInfoModel,
    linkProductsToFrontCategory,
    unlinkProductsFromFrontCategory,
    deleteMasterCategory,
    deleteFrontCategory,
    deleteProduct,
    dispatchDeferred,
    dispatchHistory,
    callBuildCategoriesCacheFunction,
    callBuildProductCacheFunction,
    createImportSpreadsheet,
    createImportImage,
    flushHistory,
    updateProductViaUi,
    unlinkAttributesFromInfoModel,
    createMasterCategoryFullness,
    createHistory,
    getGrids,
    getGridGroups,
    getGroups,
    getGroupImages,
    getGroupCategories,
    getCategories,
    getCategoryImages,
    getCategoryFrontCategories,
    createGrid,
    createGroup,
    linkGroupToGrid,
    createCategory,
    linkCategoryToGroup,
    linkFrontCategoryToCategory,
    createImageCache,
    createProductCombo,
    getProductCombos,
    createProductComboGroup,
    createProductComboOption,
    linkProductsToProductCombo,
    deleteProductCombo,
    getAttributeGroups,
    getAttributeGroupById,
    getAttributesByGroupId,
    linkAttributesToGroup,
    createAttributeGroup,
    updateAttributeGroup,
    createRole,
    getRoles,
    createUserRole,
    getUserRole,
    getUserRoles,
    getProductConfirmation
};

type AttributeProps = {
    options?: DeepPartial<AttributeOption>[];
};

export async function attributesFactory(
    user: User,
    attributes: readonly (DeepPartial<Attribute> & {properties?: AttributeProps})[]
): Promise<Attribute[]> {
    const res: Attribute[] = [];
    for (const attribute of attributes) {
        const newAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute
        });
        res.push(newAttr);

        const options = attribute.properties?.options;
        if (options) {
            for (const {code} of options) {
                await TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {code, attributeId: newAttr.id}
                });
            }
        }
    }
    return res;
}

export async function infoModelsFactory(
    user: User,
    region: Region,
    attributesGroups: readonly AttributeShort[][]
): Promise<InfoModel[]> {
    const res: InfoModel[] = [];
    for (const attributes of attributesGroups) {
        res.push(
            await TestFactory.createInfoModel({
                userId: user.id,
                regionId: region.id,
                attributes
            })
        );
    }
    return res;
}

import type {I18nType} from '@lavka-birds/i18n';
import type {Staff} from '@lavka-js-toolbox/staff-provider';
import {address, first_name, last_name, seed, sentence, username, uuid} from 'casual';

import {AnalystEntitiesIntervalsEntity} from '@/src/entities/analyst-entities-intervals/entity';
import {AnalystForecastOrdersEntity} from '@/src/entities/analyst-forecast-orders/entity';
import {AnalystHexEntity} from '@/src/entities/analyst-hex/entity';
import {AnalystHexSocdemEntity} from '@/src/entities/analyst-hex-socdem/entity';
import {AnalystStoreRoutingEntity} from '@/src/entities/analyst-store-routing/entity';
import {CandidateEntity} from '@/src/entities/candidate/entity';
import {CandidateStepEntity} from '@/src/entities/candidate-step/entity';
import {CandidateStepActionEntity} from '@/src/entities/candidate-step-action/entity';
import {CandidateStepActionFilesEntity} from '@/src/entities/candidate-step-action-files/entity';
import {CandidateTagsEntity} from '@/src/entities/candidate-tags/entity';
import {CandidateToTagEntity} from '@/src/entities/candidate-to-tag/entity';
import {CityEntity} from '@/src/entities/city/entity';
import {RegionDefaultCityEntity} from '@/src/entities/default-city/entity';
import {EntitiesGroupEntity} from '@/src/entities/entities-group/entity';
import {HexOrdersEntity} from '@/src/entities/hex-orders/entity';
import {LangEntity} from '@/src/entities/lang/entity';
import {ManagerPointEntity} from '@/src/entities/manager-point/entity';
import {ManagerZoneEntity} from '@/src/entities/manager-zone/entity';
import {ManagerZoneAnalyticsEntity} from '@/src/entities/manager-zone-analytics/entity';
import {RegionEntity} from '@/src/entities/region/entity';
import {SearchHistoryEntity} from '@/src/entities/search-history/entity';
import {UserEntity} from '@/src/entities/user/entity';
import {UserRolesEntity} from '@/src/entities/user-roles/entity';
import {WmsStoreEntity} from '@/src/entities/wms-stores/entity';
import {WmsZoneAnalyticsEntity} from '@/src/entities/wms-zone-analytics/entity';
import {WmsZoneEntity} from '@/src/entities/wms-zones/entity';
import {WmsZonesOrdersEntity} from '@/src/entities/wms-zones-orders/entity';
import type {UILanguage} from '@/src/i18n';
import {formatPoint, getHexCenter} from '@/src/lib/geo';
import {ensureDbConnection, executeInTransaction} from '@/src/service/db';
import {polygon} from '@/src/service/seed-db/fixtures';
import {FEATURE_ACCESS_DEFAULT} from 'constants/idm';
import {BaseApiRequestContext, UserApiRequestContext} from 'server/routes/api/api-context';
import type {
    AnalystEntitiesIntervalsParams,
    AnalystHex,
    AnalystOrder,
    AnalystSocdemData,
    WmsZoneOrder
} from 'types/analyst';
import {AnalystEntity} from 'types/analyst';
import type {AnalystForecastOrders} from 'types/analyst-forecast-orders';
import type {AnalystStoreRouting} from 'types/analyst-store-routing';
import type {City, DefaultCity} from 'types/city';
import {
    Candidate,
    CandidateStatus,
    CandidateStep,
    CandidateStepAction,
    CandidateStepActionFile,
    CandidateStepActionType,
    CandidateStepStatus,
    CandidateTag,
    StepCode
} from 'types/crm-candidates';
import {TransactionSource} from 'types/db';
import type {EntitiesGroupType} from 'types/entities-group';
import type {ManagerZoneAnalytics, WmsZoneAnalytics} from 'types/export';
import {FeatureAccess, Role} from 'types/idm';
import type {BasicRequest} from 'types/request';
import {SearchEntity} from 'types/search';
import {DeliveryType, StoreStatus, WmsStore, WmsZone, ZoneStatus} from 'types/wms';

import {CityGeoId} from './types';

seed(3);

async function createWmsZonesAnalytics(wmsZonesAnalytics?: WmsZoneAnalytics) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(WmsZoneAnalyticsEntity);

    const wmsZonesAnalyticsEntity = manager.create(WmsZoneAnalyticsEntity, wmsZonesAnalytics);

    return manager.save(wmsZonesAnalyticsEntity);
}

async function createWmsZone(wmsZonePartial?: Partial<WmsZone>) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(WmsZoneEntity);
    const entitiesGroups = await connection
        .getRepository(EntitiesGroupEntity)
        .createQueryBuilder('entities_groups')
        .getMany();

    const someGroupId: number = entitiesGroups.length ? entitiesGroups[0].id : 1;

    const zoneEntity = manager.create(WmsZoneEntity, {
        storeId: uuid,
        id: uuid,
        groupId: someGroupId,
        zone: {
            type: 'Feature',
            geometry: {
                type: 'MultiPolygon',
                coordinates: []
            }
        },
        status: ZoneStatus.ACTIVE,
        deliveryType: DeliveryType.FOOT,
        effectiveFrom: new Date(),
        effectiveTill: undefined,
        ...wmsZonePartial
    });

    return manager.save(zoneEntity);
}

async function createWmsStore(wmsStorePartial?: Partial<WmsStore>) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(WmsStoreEntity);

    const storeEntity = manager.create(WmsStoreEntity, {
        id: uuid,
        location: {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: []
            }
        },
        status: StoreStatus.ACTIVE,
        type: 'lavka',
        title: sentence,
        address,
        cityGeoId: CityGeoId.MOSCOW,
        ...wmsStorePartial
    });

    return manager.save(storeEntity);
}

async function createUserWithUid(uid: string) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(UserEntity);

    const user = manager.create(UserEntity, {
        uid,
        login: username
    });

    await manager.save(user);

    await addRole({uid, role: Role.FULL_ACCESS});
    return manager.findOneOrFail(UserEntity, user.uid);
}

interface CreateUserOptions {
    uid?: number;
    staffData?: Staff.Person;
    role?: Role;
    skipRoleCreation?: boolean;
}

async function createUser({uid, staffData, role, skipRoleCreation}: CreateUserOptions = {}) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(UserEntity);

    const user = manager.create(UserEntity, {
        uid: typeof uid === 'number' ? String(uid) : '1',
        login: username,
        staffData: {
            name: {
                first: {
                    ru: first_name
                },
                last: {
                    ru: last_name
                }
            },
            ...staffData
        }
    });

    await manager.save(user);

    const userEntity = await manager.findOneOrFail(UserEntity, user.uid);

    if (skipRoleCreation) {
        return userEntity;
    }

    await addRole({uid: userEntity.uid, role: role || Role.FULL_ACCESS});

    return manager.findOneOrFail(UserEntity, user.uid, {relations: ['roles']});
}

interface AddRoleOptions {
    uid: string;
    role: Role;
    fields?: Partial<FeatureAccess>;
}

async function addRole({uid, role, fields}: AddRoleOptions) {
    const path = 'project.group.role.';
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(UserRolesEntity);

    const userRole = manager.create(UserRolesEntity, {
        userId: uid,
        role,
        path: `${path}${role}`,
        fields: fields || FEATURE_ACCESS_DEFAULT
    });

    await manager.save(userRole);
    return manager.findOneOrFail(UserRolesEntity, {
        userId: uid,
        role,
        path: `${path}${role}`
    });
}

// eslint-disable-next-line prettier/prettier
async function createManagerZone(
    userId: string,
    managerZoneData?: {userId: string; cityGeoId: number; zone: object; name: string; isPublished?: boolean}
) {
    return executeInTransaction({authorId: userId, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(ManagerZoneEntity);

        const managerZone = manager.create(
            ManagerZoneEntity,
            managerZoneData || {zone: {}, cityGeoId: CityGeoId.MOSCOW, userId: '1'}
        );

        await manager.save(managerZone);

        return repository.findOneOrFail(managerZone.id);
    });
}

async function createManagerZoneAnalytics(zoneAnalytics?: ManagerZoneAnalytics) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(ManagerZoneAnalyticsEntity);

    const zoneAnalyticsEntity = manager.create(ManagerZoneAnalyticsEntity, zoneAnalytics);

    return manager.save(zoneAnalyticsEntity);
}

async function createAnalystStoreRouting(userId: string, analystStoreRouting?: AnalystStoreRouting) {
    return executeInTransaction({authorId: userId, source: 'ui'}, async (manager) => {
        const analystStoreRoutingEntity = manager.create(AnalystStoreRoutingEntity, analystStoreRouting);

        return manager.save(analystStoreRoutingEntity);
    });
}

async function createAnalystForecastOrders(userId: string, analystStoreRouting?: AnalystForecastOrders) {
    return executeInTransaction({authorId: userId, source: 'ui'}, async (manager) => {
        const analystForecastOrdersEntity = manager.create(AnalystForecastOrdersEntity, analystStoreRouting);

        return manager.save(analystForecastOrdersEntity);
    });
}

async function createEntitiesGroup(userId: string, entitiesGroupData?: {name: string; groupType: EntitiesGroupType}) {
    return executeInTransaction({authorId: userId, source: 'ui'}, async (manager) => {
        const entitiesGroup = manager.create(EntitiesGroupEntity, {id: 1, ...entitiesGroupData});

        return await manager.save(entitiesGroup);
    });
}

async function createManagerPoint(
    userId: string,
    managerZoneData?: {userId: string; cityGeoId: number; point: [number, number]; name: string; isPublished?: boolean}
) {
    return executeInTransaction({authorId: userId, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(ManagerPointEntity);

        const createManagerPoint = manager.create(
            ManagerPointEntity,
            managerZoneData || {point: [32, 34], cityGeoId: CityGeoId.MOSCOW, userId: '1', name: 'test name'}
        );

        await manager.save(createManagerPoint);

        return repository.findOneOrFail(createManagerPoint.id);
    });
}

async function createHex(hexData?: AnalystHex<string>) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(AnalystHexEntity);

    const center = formatPoint(getHexCenter(hexData ? hexData.id : '23123'));
    const hex = manager.create(
        AnalystHexEntity,
        hexData
            ? {...hexData, center}
            : {
                  id: '23123',
                  polygon,
                  center,
                  city: 'Moscow',
                  cityGeoId: CityGeoId.MOSCOW
              }
    );

    await manager.save(hex);

    return manager.findOneOrFail(AnalystHexEntity, hex.id);
}

interface CreateRegionParams {
    code?: string;
    defaultCityGeoId?: CityGeoId;
}

async function createRegion(params: CreateRegionParams = {}) {
    const connection = await ensureDbConnection();

    const {manager} = connection.getRepository(RegionEntity);

    const region = manager.create(RegionEntity, {
        id: 1,
        isoCode: (params.code || uuid).toUpperCase()
    });

    const regionCreated = await manager.save(region);

    const defaultCityGeoId = params.defaultCityGeoId || CityGeoId.MOSCOW;
    try {
        await createCity({id: defaultCityGeoId});
    } catch (err) {
        // skip
    }
    try {
        await createDefaultCity({cityId: defaultCityGeoId, regionId: regionCreated.id});
    } catch (err) {
        // skip
    }

    return manager.findOneOrFail(RegionEntity, regionCreated.id);
}

async function createCity(params: Partial<City> = {}) {
    const connection = await ensureDbConnection();

    const {manager} = connection.getRepository(CityEntity);

    const city = manager.create(CityEntity, {
        id: CityGeoId.MOSCOW,
        nameEn: 'nameEn',
        nameRu: 'имяРу',
        cityPoint: '',
        hasImportedHexes: true,
        regionId: 1,
        ...params
    });

    return manager.save(city);
}

async function createDefaultCity(params: Partial<DefaultCity> = {}) {
    const connection = await ensureDbConnection();

    const {manager} = connection.getRepository(RegionDefaultCityEntity);

    const city = manager.create(RegionDefaultCityEntity, {
        cityId: CityGeoId.MOSCOW,
        regionId: 1,
        ...params
    });

    return manager.save(city);
}

async function createLang({isoCode = uuid}: {isoCode?: string} = {}) {
    const connection = await ensureDbConnection();

    const {manager} = connection.getRepository(LangEntity);

    const lang = manager.create(LangEntity, {id: 1, isoCode});

    await manager.save(lang);

    return manager.findOneOrFail(LangEntity, lang.id);
}

async function createCandidate(uid: string, candidateData?: Partial<Candidate>) {
    return executeInTransaction({authorId: uid, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(CandidateEntity);

        const candidateEntity = repository.create({
            name: 'Warehouse 1',
            status: CandidateStatus.PROGRESS,
            description: 'Test',
            cityGeoId: CityGeoId.MOSCOW,
            responsibleUserId: uid,
            ...candidateData
        });

        await repository.save(candidateEntity);

        return candidateEntity;
    });
}

async function createCandidateTag(uid: string, tagData?: Partial<CandidateTag>) {
    return executeInTransaction({authorId: uid, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(CandidateTagsEntity);

        const candidateTagEntity = repository.create({name: 'Test tag', userId: uid, ...tagData});

        await repository.save(candidateTagEntity);

        return candidateTagEntity;
    });
}

async function createCandidateToTag(uid: string, candidateToTagData?: {candidateId: string; candidateTagId: string}) {
    return executeInTransaction({authorId: uid, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(CandidateToTagEntity);

        const createCandidateToTag = manager.create(
            CandidateToTagEntity,
            candidateToTagData || {candidateId: '1', candidateTagId: '1'}
        );

        await manager.save(createCandidateToTag);

        return repository.findOneOrFail(createCandidateToTag.id);
    });
}

async function createCandidateStep(uid: string, candidateStepData?: Partial<CandidateStep>) {
    return executeInTransaction({authorId: uid, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(CandidateStepEntity);

        const candidateStepEntity = repository.create({
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_1_1,
            responsibleUserId: uid,
            ...candidateStepData
        });

        await repository.save(candidateStepEntity);

        return candidateStepEntity;
    });
}

async function createCandidateStepAction(uid: string, candidateStepActionData?: Partial<CandidateStepAction>) {
    return executeInTransaction({authorId: uid, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(CandidateStepActionEntity);

        const candidateStepActionEntity = repository.create({
            candidateStepId: '1',
            userId: uid,
            type: CandidateStepActionType.COMMENT,
            comment: 'Comment',
            ...candidateStepActionData
        });

        await repository.save(candidateStepActionEntity);

        return candidateStepActionEntity;
    });
}

async function createCandidateStepActionFile(
    uid: string,
    candidateStepActionFileData?: Partial<CandidateStepActionFile>
) {
    return executeInTransaction({authorId: uid, source: 'import'}, async (manager) => {
        const repository = manager.getRepository(CandidateStepActionFilesEntity);

        const candidateStepActionFileEntity = repository.create({
            groupId: '1',
            name: 'Test',
            ...candidateStepActionFileData
        });

        await repository.save(candidateStepActionFileEntity);

        return candidateStepActionFileEntity;
    });
}

interface CreateApiContextParams {
    params?: Record<string, string>;
    query?: Record<string, string>;
    body?: unknown;
    user?: UserEntity;
    region?: RegionEntity;
    lang?: LangEntity;
}

interface TestUserApiRequestContextParams extends CreateApiContextParams {
    user: UserEntity;
    region: RegionEntity;
    lang: LangEntity;
}

class TestUserApiRequestContext extends UserApiRequestContext {
    params: TestUserApiRequestContextParams;

    constructor(params: TestUserApiRequestContextParams) {
        super({} as BasicRequest);
        this.params = params;
    }

    getParams = () => this.params.params || {};
    getQuery = () => this.params.query || {};
    getBody = () => this.params.body;
    getUser = () => this.params.user;
    getRegion = async () => this.params.region;
    getRegionCode = () => this.params.region.isoCode;
    getLang = async () => this.params.lang;
    getLangCode = () => this.params.lang.isoCode as UILanguage;
    getI18n = (): I18nType => {
        return function (keySet: string, key: string) {
            return `${keySet}-${key}`;
        };
    };

    get meta() {
        return {
            authorId: this.params.user.uid,
            source: TransactionSource.UI
        };
    }

    get user() {
        return this.params.user;
    }
}

async function createUserApiContext(params: CreateApiContextParams = {}) {
    return new TestUserApiRequestContext({
        ...params,
        user: params.user ?? (await createUser()),
        lang: params.lang ?? (await createLang()),
        region: params.region ?? (await createRegion())
    });
}

interface TestBaseApiRequestContextParams extends CreateApiContextParams {
    lang: LangEntity;
}

class TestBaseApiRequestContext extends BaseApiRequestContext {
    params: TestBaseApiRequestContextParams;

    constructor(params: TestBaseApiRequestContextParams) {
        super({} as BasicRequest);
        this.params = params;
    }

    getParams = () => this.params.params || {};
    getQuery = () => this.params.query || {};
    getBody = () => this.params.body;
    getLang = async () => this.params.lang;
    getLangCode = () => this.params.lang.isoCode as UILanguage;
    getI18n = (): I18nType => {
        return function (keySet: string, key: string) {
            return `${keySet}-${key}`;
        };
    };
}

async function createBaseApiContext(params: CreateApiContextParams = {}) {
    return new TestBaseApiRequestContext({
        ...params,
        lang: params.lang ?? (await createLang())
    });
}

async function createSocdem(socdemData?: {hexId: string; socdem: Partial<AnalystSocdemData>}) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(AnalystHexSocdemEntity);

    const socdem = manager.create(AnalystHexSocdemEntity, socdemData || {hexId: '23123', socdem: {}});

    await manager.save(socdem);

    return manager.findOneOrFail(AnalystHexEntity, socdem.hexId);
}

async function createIntervals(intervalsData?: Partial<AnalystEntitiesIntervalsParams>) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(AnalystEntitiesIntervalsEntity);

    const intervals = manager.create(AnalystEntitiesIntervalsEntity, {
        entity: AnalystEntity.SOCDEM_C1C2RES,
        cityGeoId: CityGeoId.MOSCOW,
        intervals: [1, 49, 143, 258, 433, 1053],
        ...intervalsData
    });

    await manager.save(intervals);

    return manager.findOneOrFail(AnalystEntitiesIntervalsEntity, {
        cityGeoId: intervals.cityGeoId,
        entity: intervals.entity
    });
}

async function createSearchHistory(
    userId: string,
    entityData?: {id: string; type: SearchEntity; cityGeoId: number; name: string}
) {
    return executeInTransaction({authorId: userId, source: 'ui'}, async (manager) => {
        const repository = manager.getRepository(SearchHistoryEntity);

        const addSearchHistory = manager.create(SearchHistoryEntity, {
            userId,
            entityData: entityData || {
                id: '1',
                type: SearchEntity.MANAGER_POINTS,
                cityGeoId: CityGeoId.MOSCOW,
                name: 'name'
            },
            updatedAt: new Date()
        });

        await manager.save(addSearchHistory);

        return repository.findOneOrFail(addSearchHistory.id);
    });
}

async function createHexOrders(hexOrders: AnalystOrder[]) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(HexOrdersEntity);

    const entities = hexOrders.map((hexOrder) => manager.create(HexOrdersEntity, hexOrder));

    await manager.save(entities);
}

async function createWmsZoneOrders(zoneOrders: WmsZoneOrder[]) {
    const connection = await ensureDbConnection();
    const {manager} = connection.getRepository(WmsZonesOrdersEntity);

    const entities = zoneOrders.map((zoneOrder) => manager.create(WmsZonesOrdersEntity, zoneOrder));

    await manager.save(entities);
}

export const TestFactory = {
    createSocdem,
    createHex,
    createUserApiContext,
    createBaseApiContext,
    createRegion,
    createCity,
    createUser,
    createManagerZone,
    createManagerZoneAnalytics,
    createWmsZone,
    createWmsStore,
    createManagerPoint,
    createWmsZonesAnalytics,
    createIntervals,
    createUserWithUid,
    createSearchHistory,
    createHexOrders,
    createWmsZoneOrders,
    createEntitiesGroup,
    createAnalystStoreRouting,
    createAnalystForecastOrders,
    createCandidate,
    createCandidateTag,
    createCandidateToTag,
    createCandidateStep,
    createCandidateStepAction,
    createCandidateStepActionFile
};

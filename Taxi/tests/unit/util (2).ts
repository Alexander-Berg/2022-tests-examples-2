import {seed, uuid} from 'casual';
import {TestFactory} from 'tests/unit/test-factory';

seed(3);

export async function madeJsonError(callback: () => unknown) {
    try {
        await callback();
    } catch (e) {
        return JSON.parse(e.message);
    }
}

export async function createSelectOptions({userId, attributeId}: {userId: number; attributeId: number}) {
    const optionCodes = [uuid, uuid, uuid];

    await Promise.all(
        optionCodes.map((code, sortOrder) =>
            TestFactory.createAttributeOption({
                userId,
                attributeOption: {attributeId, code, sortOrder}
            })
        )
    );

    return {optionCodes};
}

export async function createMasterCategoryWithInfoModel({
    infoModel: infoModelOptions,
    masterCategory: masterCategoryOptions
}: {
    infoModel?: {
        code?: string;
    };
    masterCategory?: {
        parentId?: number;
        code?: string;
    };
} = {}) {
    const user = await TestFactory.createUser();
    const region = await TestFactory.createRegion();
    const role = await TestFactory.createRole({product: {canEdit: true}});
    await TestFactory.createUserRole({
        userId: user.id,
        roleId: role.id,
        regionId: region.id
    });

    const infoModel = await TestFactory.createInfoModel({
        userId: user.id,
        regionId: region.id,
        infoModel: {
            code: infoModelOptions?.code,
            attributes: []
        }
    });

    const masterCategory = await TestFactory.createMasterCategory({
        userId: user.id,
        regionId: region.id,
        infoModelId: infoModel.id,
        parentId: masterCategoryOptions?.parentId,
        code: masterCategoryOptions?.code
    });

    return {user, role, region, infoModel, masterCategory};
}

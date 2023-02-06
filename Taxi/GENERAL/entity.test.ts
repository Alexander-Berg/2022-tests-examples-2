import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {User} from '@/src/entities/user/entity';
import {AttributeType} from 'types/attribute';

describe('"attribute" entity', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should handle attribute "is_unique" persistence', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await expect(
            TestFactory.updateAttribute(stringAttr.id, {
                userId: user.id,
                attribute: {isUnique: true}
            })
        ).rejects.toThrow('IS_UNIQUE_UPDATE_IS_FORBIDDEN');
    });

    it('should handle attribute "is_value_localizable" persistence', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await expect(
            TestFactory.updateAttribute(stringAttr.id, {
                userId: user.id,
                attribute: {isValueLocalizable: true}
            })
        ).rejects.toThrow('IS_VALUE_LOCALIZABLE_UPDATE_IS_FORBIDDEN');
    });
});

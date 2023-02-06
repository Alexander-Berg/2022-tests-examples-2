import {regions, users} from 'tests/e2e/seed-db-map';
import {v4 as uuidv4} from 'uuid';

import {DbTable} from '@/src/entities/const';
import {USER_LOGIN} from 'service/seed-db/fixtures';
import type {RegionCode} from 'types/region';
import type {RoleNameTranslationMap, Rules} from 'types/role';

interface AddUserRoleOptions {
    rules: Rules;
    region?: Exclude<Lowercase<RegionCode>, 'by' | 'za'> | null;
    nameTranslationMap?: RoleNameTranslationMap;
    clear?: boolean;
}

const defaultNameTranslationMap: RoleNameTranslationMap = {
    ru: 'Тестовая роль',
    en: 'Test role'
};

async function addUserRole(this: WebdriverIO.Browser, {rules, region, nameTranslationMap, clear}: AddUserRoleOptions) {
    if (clear) {
        await this.executeSql(
            `
            DELETE FROM ${DbTable.USER_ROLE}
            WHERE user_id = ${users[USER_LOGIN]}
            `
        );
    }

    const [role] = await this.executeSql<{id: number}[]>(
        `
        INSERT INTO ${DbTable.ROLE} (code, rules, name_translation_map)
        VALUES (
            '${uuidv4()}',
            '${JSON.stringify(rules)}'::jsonb,
            '${JSON.stringify(nameTranslationMap ?? defaultNameTranslationMap)}'::jsonb
        )
        RETURNING id;
        `
    );

    if (region) {
        await this.executeSql(
            `
            INSERT INTO ${DbTable.USER_ROLE} (user_id, role_id, region_id)
            VALUES ('${users[USER_LOGIN]}', ${role.id}, ${regions[region]});
            `
        );
    } else {
        await this.executeSql(
            `
            INSERT INTO ${DbTable.USER_ROLE} (user_id, role_id, region_id)
            VALUES ('${users[USER_LOGIN]}', ${role.id}, null);
            `
        );
    }
}

export default addUserRole;
export type AddUserRole = typeof addUserRole;

import {regions, users} from 'tests/e2e/seed-db-map';
import {v4 as uuidv4} from 'uuid';

import {DbTable} from '@/src/entities/const';
import {USER_LOGIN} from 'service/seed-db/fixtures';
import type {RegionCode} from 'types/region';
import type {RoleNameTranslationMap, Rules} from 'types/role';

interface UpdateRoleOptions {
    rules: Rules;
    region?: Exclude<Lowercase<RegionCode>, 'by' | 'za'> | null;
}

const defaultNameTranslationMap: RoleNameTranslationMap = {
    ru: 'Тестовая роль',
    en: 'Test role'
};

async function upsertRole(this: WebdriverIO.Browser, {rules, region}: UpdateRoleOptions) {
    const [role] = await this.executeSql<{id: number}[]>(
        `
        INSERT INTO ${DbTable.ROLE} (code, rules, name_translation_map)
        VALUES ('${uuidv4()}', '${JSON.stringify(rules)}'::jsonb, '${JSON.stringify(defaultNameTranslationMap)}'::jsonb)
        RETURNING id;
        `
    );

    if (region) {
        await this.executeSql<number[]>(
            `
            INSERT INTO ${DbTable.USER_ROLE} (user_id, role_id, region_id)
            VALUES ('${users[USER_LOGIN]}', ${role.id}, ${regions[region]});
            `
        );
    } else {
        await this.executeSql(
            `
            UPDATE ${DbTable.USER_ROLE}
            SET role_id = ${role.id}
            WHERE user_id = ${users[USER_LOGIN]} AND region_id IS NULL;
            `
        );
    }
}

export default upsertRole;
export type UpsertRole = typeof upsertRole;

import {getDbPathFromIdmPath, getIdmPathFromDbPath, getRoleFromIdmPath} from 'server/utils/path-helper';
import {Role} from 'types/idm';

describe('test path helper', () => {
    it('it should be get role', () => {
        const idmPath = `/project/group/role/${Role.FULL_ACCESS}/`;
        const result = getRoleFromIdmPath(idmPath);
        expect(result).toEqual(Role.FULL_ACCESS);
    });

    it('it should be get idm path', () => {
        const idmPath = `/project/group/role/${Role.FULL_ACCESS}/`;
        const result = getDbPathFromIdmPath(idmPath);
        expect(result).toEqual(`project.group.role.${Role.FULL_ACCESS}`);
    });

    it('it should be get db path', () => {
        const idmPath = `project.group.role.${Role.FULL_ACCESS}`;
        const result = getIdmPathFromDbPath(idmPath);
        expect(result).toEqual(`/project/group/role/${Role.FULL_ACCESS}/`);
    });
});

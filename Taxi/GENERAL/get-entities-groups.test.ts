import {getEntitiesGroupsHandler} from './get-entities-groups';

describe('getGroupsHandler()', () => {
    it('should return all existing entities groups', async () => {
        let {groups} = await getEntitiesGroupsHandler();

        groups = groups.filter(
            (group) => group.groupType === 'wms_zone_active' || group.groupType === 'wms_zone_disabled'
        );

        expect(groups).toHaveLength(2);
    });
});

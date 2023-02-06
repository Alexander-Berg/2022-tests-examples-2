import {groupSubventionsByRegions} from '../selectors';

const subventions: any = [
    {tariffzone: 'region1'},
    {tariffzone: 'region1'},
    {tariffzone: 'region2'},
    {tariffzone: 'region2'},
    {tariffzone: 'region3'}
];

const subventionsRes = [
    {id: 'region1', text: 'region1', url: '/subventions/geoarea/region1/?activeTab=subventions'},
    {id: 'region2', text: 'region2', url: '/subventions/geoarea/region2/?activeTab=subventions'},
    {id: 'region3', text: 'region3', url: '/subventions/geoarea/region3/?activeTab=subventions'}
];

const filter = 'on2';
const filter2 = 'щт2';

const subventionsResByFilter = [
    {id: 'region2', text: 'region2', url: '/subventions/geoarea/region2/?activeTab=subventions'}
];

describe('groupSubventionsByRegions', function () {
    test('groupSubventionsByRegions, фильтр пустой', () => {
        expect(groupSubventionsByRegions(subventions, '', 'subventions')).toEqual(subventionsRes);
    });
    test('groupSubventionsByRegions, фильтр не определён', () => {
        expect(groupSubventionsByRegions(subventions, undefined, 'subventions')).toEqual(subventionsRes);
    });
    test('groupSubventionsByRegions с фильтром', () => {
        expect(groupSubventionsByRegions(subventions, filter, 'subventions')).toEqual(subventionsResByFilter);
    });
    test('groupSubventionsByRegions, фильтр с русскими буквами', () => {
        expect(groupSubventionsByRegions(subventions, filter2, 'subventions')).toEqual(subventionsResByFilter);
    });
});

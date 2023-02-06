import {makeParamsForRoute} from '../makeParamsForRoute';

type RouteParams = {
    mode: string;
    draftId: string;
    formType: string;
};

describe('makeParamsForRoute', () => {
    it('Должен собрать часть url с указанными параметрами', () => {
        const result = makeParamsForRoute<RouteParams>(['formType', 'mode', 'draftId']);
        expect(result).toEqual(':formType?/:mode?/:draftId?');
    });
});

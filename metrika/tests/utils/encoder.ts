export type TestParams = [string, any][]
export const encodeParams = (params: TestParams) => {
    let strParams = '';
    for (var i = 0; i < params.length; i++) {
        const key = params[i][0];
        const val = params[i][1];
        strParams += (i ? '&' : '') + (key + '=' + val);
    }
    return 'https://mc.yandex.ru/collect?' + strParams;
}
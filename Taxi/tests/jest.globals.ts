/* Реэкспорт глобальных функции jest с явным указанием типа, чтобы не конфликтовали с hermione / mocha */

interface Global {
    describe: jest.Describe;
    it: jest.It;

    beforeAll: jest.Lifecycle;
    afterAll: jest.Lifecycle;
    beforeEach: jest.Lifecycle;
    afterEach: jest.Lifecycle;
    expect: jest.Expect;
}

declare const global: Global;

const describe = global.describe;
const it = global.it;
const beforeAll = global.beforeAll;
const afterAll = global.afterAll;
const beforeEach = global.beforeEach;
const afterEach = global.afterEach;
const expect = global.expect;

export {describe, it, beforeAll, afterAll, beforeEach, afterEach, expect};

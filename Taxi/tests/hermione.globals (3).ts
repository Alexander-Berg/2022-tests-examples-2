/* Реэкспорт глобальных функции hermione / mocha с явным указанием типа, чтобы не конфликтовали с jest */

import chai, {expect} from 'chai';
import matchSnapshot from 'tests/e2e/matchers/match-snapshot';

chai.use(matchSnapshot);

interface Global {
    describe: Hermione.TestDefinition;
    it: Hermione.TestDefinition;
}

declare const global: Global;

const describe = ((...args) => global.describe(...args)) as Hermione.TestDefinition;
const it = ((...args) => global.it(...args)) as Hermione.TestDefinition;

export {it, describe, expect};

const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');
/* Этот файл нужен, чтобы в тестах работал should */
chai.should();
chai.use(chaiJestSnapshot);

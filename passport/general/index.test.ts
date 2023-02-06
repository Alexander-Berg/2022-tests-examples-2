import { IpregController } from '.';
import {
  expectedUserNets,
  expectedYandexNets,
  externalAddresses,
  internalAddresses,
} from './test-data/expectance';

let ipreg: IpregController;

beforeAll(() => {
  ipreg = new IpregController('./src/test-data/2948816849.json');
});

describe('Выпаршивает правильные подсети', () => {
  test('яндексовые', () => {
    expect(ipreg.yandexNets.map((n) => n.toString())).toEqual(expectedYandexNets);
  });

  test('пользовательские', () => {
    expect(ipreg.userNets.map((n) => n.toString())).toEqual(expectedUserNets);
  });
});

describe('Правильно определяет сети', () => {
  describe('Внутренние', () => {
    internalAddresses.forEach((addr, idx) => {
      test(`${idx}: ${addr}`, () => expect(ipreg.isYandexAddr(addr)).toStrictEqual(true));
    });
  });

  describe('Внешние', () => {
    externalAddresses.forEach((addr, idx) => {
      test(`${idx}: ${addr}`, () => expect(ipreg.isYandexAddr(addr)).toStrictEqual(false));
    });
  });

  describe('Пользовательские', () => {
    test(`0: 5.45.210.1`, () => expect(ipreg.isUserAddr('5.45.210.1')).toStrictEqual(true));
    test(`1: 2a02:6b8:b081:214:1::`, () =>
      expect(ipreg.isUserAddr('2a02:6b8:b081:214:1::')).toStrictEqual(true));
  });
});

import Chance from 'chance';

const chance = new Chance();

export const getRandomName = (max = 256) => {
    const length = chance.natural({ max, min: 2 });
    return chance.string({ length });
};

export const getRandomInteger = (max = 100, min = 0) => {
    return chance.natural({ max, min });
};

export const escapeRegExp = (str: string) => {
    return str.replace(/[\-[\]/{}()*+?.\\^$|]/g, '\\$&');
};

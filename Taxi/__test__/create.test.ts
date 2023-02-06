import {makeModel} from '../';

interface TestFormModel {
    login: string;
    name: string;
    age: number;
    date: {
        day: string;
        month: string;
        year: string;
    };
}

test('makeModel should return correct string', () => {
    expect(makeModel<TestFormModel>(m => m.name)).toBe('name');
});

test('makeModel should return correct string with nested block', () => {
    expect(makeModel<TestFormModel>(m => m.date.day)).toBe('date.day');
});

test('makeModel should return correct string with nested any block', () => {
    expect(makeModel<any>(m => m.foo.bar.test.long)).toBe('foo.bar.test.long');
});

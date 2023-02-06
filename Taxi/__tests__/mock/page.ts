import {
    findElement,
    findByData,
    findByText,
    findText,
    findMultipleElements,
    findMultipleByData,
    findMultipleByText,
    findMultiplyText,
    Undefinable,
} from '../../src';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface String {
    waitForExist(): Promise<void>;
    getText(): Promise<string>;
}

// @ts-ignore
String.prototype.waitForExist = function () {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(`${this}_waited`);
        }, 42);
    });
};

// @ts-ignore
String.prototype.getText = function () {
    return Promise.resolve(`${this}_result`);
};

async function selector(query: string) {
    return Promise.resolve(`prefix_${query}`);
}

async function multiplySelector(query: string) {
    return Promise.resolve([
        `prefix_2_${query}`,
        `prefix_1_${query}`,
    ]);
}

class Page {
    public selector(query: string) {
        return selector(query);
    }

    public multiplySelector(query: string) {
        return multiplySelector(query);
    }
}

/*
* класс для примера работы с декораторами
* теперь не нужно писать get funcName() { return $(...); }
* вместо этого можно использовать готовые декораторы
* */
class SomePage extends Page {
    // здесь сразу будет поиск по [data-cy=""], не нужно писать обрамление руками
    @findByData('schedules-card-card_picker-complexity_simple-button-create')
    public findByData_1: Undefinable<Promise<string>>;

    @findByText('test_test')
    public findByText_1: Undefinable<Promise<string>>;

    @findText('test_test')
    public findText_1: Undefinable<Promise<string>>;

    // тут вы можете искать как обычно искали бы через $
    @findElement('#simplePattern_1_even')
    public findElement_1: Undefinable<Promise<string>>;
    @findElement('')
    public findElement_2: Undefinable<Promise<string>>;

    @findMultipleElements('#simplePattern_1_even')
    public findMultipleElements_1: Undefinable<Promise<string[]>>;

    @findMultipleByData('#simplePattern_1_even')
    public findMultipleByData_1: Undefinable<Promise<string[]>>;

    @findMultipleByText('#simplePattern_1_even')
    public findMultipleByText_1: Undefinable<Promise<string[]>>;

    @findMultiplyText('#simplePattern_1_even')
    public findMultiplyText_1: Undefinable<Promise<string[]>>;
}

export const somePage = new SomePage();

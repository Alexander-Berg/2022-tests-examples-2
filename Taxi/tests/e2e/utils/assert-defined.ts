/**
 * @function
 * @description Проверят что элемент не `null` и не `undefined`, в противном случае бросает ошибку
 * @param item
 * @param message
 * @returns
 */
export default function assertDefined<T extends unknown>(item: T, message?: string): NonNullable<T> {
    if (typeof item === 'undefined' || item === null) {
        throw new Error(message ?? `Expected value to be defined, but received: ${item}`);
    }
    return item as NonNullable<T>;
}

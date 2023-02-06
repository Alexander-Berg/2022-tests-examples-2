/* eslint-disable @typescript-eslint/no-non-null-assertion */
import type {Attribute} from '../attribute/entity';
import type {ProductAttributeValue} from '../product-attribute-value/entity';
import type {History} from './entity';

it('always passes', () => expect(true).toBeTruthy());

if (false as boolean) {
    // Это тест для TypeScript.
    // Код здесь никогда не выполнится. Он нужен для проверки правильного выведения типов.
    // Если файл компилируется, значит тест проходит!

    // Проверки выглядят так:
    // если undefined включён в foo, тест проходит; иначе, падает
    // undefined extends foo ? Pass : Fail
    //
    // Для более узкого (narrow) сравнения, можно изменить условие
    // если foo включён в 't' или 'f', тест проходит; иначе, падает
    // foo extends 't' | 'f' ? Pass : Fail

    type Pass = {ok: unknown};
    type Fail = null;
    type Assert<T extends Pass> = T['ok']; // ОК! если успешно доступиться до метода строки

    const attribute = ({} as History<Attribute>).newRow!;

    {
        const {ticket} = attribute;

        type MayContainUndefined = undefined extends typeof ticket ? Pass : Fail;
        let _: Assert<MayContainUndefined>;

        type MayContainNull = null extends typeof ticket ? Pass : Fail;
        let __: Assert<MayContainNull>;

        // @ts-expect-error string != number
        ticket as number;
    }

    {
        const {is_value_localizable} = attribute;
        type MayContainUndefined = undefined extends typeof is_value_localizable ? Pass : Fail;
        let _: Assert<MayContainUndefined>;

        excludeUndefined(is_value_localizable); // ('t' | 'f' | undefined) => ('t' | 'f')
        type OnlyContainsTF = typeof is_value_localizable extends 't' | 'f' ? Pass : Fail;
        let __: Assert<OnlyContainsTF>;
    }

    {
        const {code} = attribute;

        type MayContainUndefined = undefined extends typeof code ? Pass : Fail;
        let _: Assert<MayContainUndefined>;

        type MayNotContainNull = null extends typeof code ? Fail : Pass;
        let __: Assert<MayNotContainNull>;
    }

    const pav = ({} as History<ProductAttributeValue>).newRow!;

    {
        const {attribute_id} = pav;

        type MayContainUndefined = undefined extends typeof attribute_id ? Pass : Fail;
        let _: Assert<MayContainUndefined>;

        type MayNotContainNull = null extends typeof attribute_id ? Fail : Pass;
        let __: Assert<MayNotContainNull>;

        // @ts-expect-error string != number
        attribute_id as number;
    }

    {
        const {lang_id} = pav;

        type MayContainUndefined = undefined extends typeof lang_id ? Pass : Fail;
        let _: Assert<MayContainUndefined>;

        type MayContainNull = null extends typeof lang_id ? Pass : Fail;
        let __: Assert<MayContainNull>;

        // @ts-expect-error string != number
        lang_id as number;
    }
}

declare function excludeUndefined<T>(val: T): asserts val is Exclude<T, undefined>;

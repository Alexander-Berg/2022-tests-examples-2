import { Browser } from 'hermione';

// moveTo является deprecate и не поддерживается, например, файрфоксом.
// Но в то же время его рекомендуемая алтернатива actions так же поддерживается еще не всеми.
// Так что если в будущем с этим начнут возникать проблемы, то здесь можно будет править логику не меняя тесты.
const customMoveTo: Browser['customMoveTo'] = function(
    this: Browser,
    selector?: string,
) {
    return this.element(selector!).then((res) => {
        return this.moveTo<null>(res.value.ELEMENT);
    });
};

export { customMoveTo };

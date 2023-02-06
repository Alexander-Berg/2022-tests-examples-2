type Coordinates = {x: number; y: number};
interface Options {
    coordinates?: Coordinates;
    targetSelector?: Hermione.GenericSelector;
}

/**
 * @function
 * @description Выполняет drag&drop элемента
 * @param this
 * @param selector
 * @param options
 */
export async function dragAndDrop(this: WebdriverIO.Browser, selector: Hermione.GenericSelector, options?: Options) {
    const {targetSelector, coordinates = {x: 0, y: 0}} = options || {};

    const element = await this.assertBySelector(selector);
    const sourceElementRect = await this.getElementRect(element.elementId);

    if (!sourceElementRect) {
        return;
    }

    const sourceX = sourceElementRect.x + sourceElementRect.width / 2;
    const sourceY = sourceElementRect.y + sourceElementRect.height / 2;

    let diffX, diffY;

    if (targetSelector) {
        const targetElement = await this.assertBySelector(targetSelector);
        const targetElementRect = await this.getElementRect(targetElement.elementId);
        const targetX = targetElementRect.x + targetElementRect.width / 2;
        const targetY = targetElementRect.y + targetElementRect.height / 2;
        diffX = targetX - sourceX + coordinates.x;
        diffY = targetY - sourceY + coordinates.y;
    } else {
        diffX = coordinates.x;
        diffY = coordinates.y;
    }

    await this.performActions([
        {
            type: 'pointer',
            id: 'drag-and-drop',
            parameters: {pointerType: 'mouse'},
            actions: [
                {type: 'pointerMove', duration: 0, x: Math.round(sourceX), y: Math.round(sourceY)},
                {type: 'pointerDown', button: 0},
                {
                    type: 'pointerMove',
                    duration: 0,
                    origin: 'pointer',
                    x: Math.round(diffX / 2),
                    y: Math.round(diffY / 2)
                },
                {type: 'pointerMove', duration: 0, origin: 'pointer', x: Math.round(diffX), y: Math.round(diffY)},
                {type: 'pointerUp', button: 0}
            ]
        }
    ]);
}

export type DragAndDrop = typeof dragAndDrop;

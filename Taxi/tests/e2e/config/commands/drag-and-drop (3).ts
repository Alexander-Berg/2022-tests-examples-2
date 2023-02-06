interface Options {
    hoverTime?: number;
    offset?: Offset;
}

type Offset = 'top' | 'bottom' | 'left' | 'right' | 'center';
type DnDEvent = 'dragstart' | 'drag' | 'dragover' | 'dragleave' | 'dragenter' | 'dragover' | 'dragend' | 'drop';
type Coordinates = {clientX: number; clientY: number};

/**
 * @function
 * @description Выполняет drag&drop одного элемента в другой
 * @param this
 * @param draggable
 * @param droppable
 * @param options
 */
async function dragAndDrop(
    this: WebdriverIO.Browser,
    draggable: Hermione.Selector,
    droppable: Hermione.Selector,
    options?: Options
) {
    const [sourceElement, targetElement] = await Promise.all([
        this.findByTestId(draggable),
        this.findByTestId(droppable)
    ]);

    await this.execute(
        function (source, target, hoverTime, offset) {
            const fireEvent = (element: Element, type: DnDEvent, coordinates?: Coordinates) => {
                const event = new CustomEvent(type, {cancelable: true, bubbles: true});
                if (coordinates) {
                    Object.assign(event, coordinates);
                }
                element.dispatchEvent(event);
            };

            const centerOf = (rect: DOMRect, axis: 'x' | 'y') => {
                const side = {x: 'width', y: 'height'} as const;
                return Math.floor(rect[axis] + rect[side[axis]] / 2);
            };

            const sourceRect = target.getBoundingClientRect();
            const targetRect = target.getBoundingClientRect();

            const dragStartPosition = {
                clientX: centerOf(sourceRect, 'x'),
                clientY: centerOf(sourceRect, 'y')
            };

            const offsetX = (({left: -1, right: 1} as never)[offset] ?? 0) * Math.floor(targetRect.width / 4);
            const offsetY = (({top: -1, bottom: 1} as never)[offset] ?? 0) * Math.floor(targetRect.height / 4);

            const dragEndPosition = {
                clientX: centerOf(targetRect, 'x') + offsetX,
                clientY: centerOf(targetRect, 'y') + offsetY
            };

            const directionX = Math.sign(dragStartPosition.clientX - dragEndPosition.clientX);
            const directionY = Math.sign(dragStartPosition.clientY - dragEndPosition.clientY);

            const draggingOnSourcePosition = {
                clientX: dragStartPosition.clientX + directionX,
                clientY: dragStartPosition.clientY + directionY
            };

            const draggingOnTargetPosition = {
                clientX: dragEndPosition.clientX - directionX,
                clientY: dragEndPosition.clientY - directionY
            };

            fireEvent(source, 'dragstart', dragStartPosition);
            fireEvent(source, 'drag', draggingOnSourcePosition);
            fireEvent(source, 'dragover', draggingOnSourcePosition);
            fireEvent(source, 'dragleave', draggingOnSourcePosition);
            fireEvent(target, 'dragenter', draggingOnTargetPosition);
            fireEvent(target, 'dragover', draggingOnTargetPosition);

            if (typeof hoverTime === 'number') {
                setTimeout(() => {
                    fireEvent(target, 'dragleave', dragEndPosition);
                    fireEvent(source, 'dragend', dragEndPosition);
                }, hoverTime);
            } else {
                fireEvent(target, 'drop', dragEndPosition);
                fireEvent(source, 'dragend', dragEndPosition);
            }
        },
        (sourceElement as unknown) as Element,
        (targetElement as unknown) as Element,
        options?.hoverTime ?? false,
        options?.offset ?? 'center'
    );
}

export default dragAndDrop;
export type DragAndDrop = typeof dragAndDrop;

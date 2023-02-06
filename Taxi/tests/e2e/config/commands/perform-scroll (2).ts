type Direction = 'up' | 'down' | 'left' | 'right';

type Delay = number | (() => Promise<void>);

type Options = {
    direction?: Direction;
    beforeIterationDelay?: Delay;
    afterIterationDelay?: Delay;
};

const DEFAULT_ITERATION_DELAY = 50;

const STABLE_ITERATIONS_COUNT = 3;

/**
 * @function
 * @description Скроллит элемент до упора в одном из направлений
 */
export default async function performScroll(this: WebdriverIO.Browser, selector: Hermione.Selector, options?: Options) {
    const element = await this.findByTestId(selector);

    const direction = options?.direction ?? 'down';
    const beforeIterationDelay = options?.beforeIterationDelay ?? DEFAULT_ITERATION_DELAY;
    const afterIterationDelay = options?.afterIterationDelay ?? DEFAULT_ITERATION_DELAY;

    const waitDelay = async (delay: Delay) => {
        if (typeof delay === 'function') {
            await delay();
        } else {
            await this.pause(delay);
        }
    };

    let previousDiff: number | null = null;
    let stableIterationsCount = 0;

    do {
        await waitDelay(beforeIterationDelay);

        const currentDiff = await this.execute(
            (element, direction) => {
                const {left, top, width, height} = element.getBoundingClientRect();
                const scrollPosition = {left, top};
                switch (direction) {
                    case 'up':
                        scrollPosition.top = -height;
                        break;
                    case 'left':
                        scrollPosition.left = -width;
                        break;
                    case 'down':
                        scrollPosition.top = height;
                        break;
                    case 'right':
                        scrollPosition.left = width;
                        break;
                    default:
                        break;
                }
                element.scrollBy({...scrollPosition});
                const {scrollTop, scrollLeft} = element;

                switch (direction) {
                    case 'up':
                    case 'down':
                        return scrollTop;
                    case 'left':
                    case 'right':
                        return scrollLeft;
                    default:
                        return null;
                }
            },
            (element as unknown) as HTMLElement,
            direction
        );

        if (currentDiff === previousDiff) {
            stableIterationsCount++;
        } else {
            stableIterationsCount = 0;
            previousDiff = currentDiff;
        }

        await waitDelay(afterIterationDelay);
    } while (stableIterationsCount < STABLE_ITERATIONS_COUNT);
}

export type PerformScroll = typeof performScroll;

/**
 * @constant
 * @description Интервал для проведения проверки
 */
const CHECK_INTERVAL_MS = 250;

/**
 * @constant
 * @description Общий таймаут на выполнение функции
 */
const TIMEOUT_MS = 5000;

/**
 * @constant
 * @description Минимальное количество стабильных итераций после которых страница считается отрендеренной
 */
const MIN_STABLE_ITERATIONS = 3;

interface WaitUntilOptions {
    minStableIterations?: number;
}

/**
 * @function
 * @description Отслеживает длину HTML при клиентском рендере,
 * если длина не меняется в течении трех итераций - страница считается полностью отрендеренной
 */
export default async function waitUntilRendered(this: WebdriverIO.Browser, options?: WaitUntilOptions) {
    const {minStableIterations = MIN_STABLE_ITERATIONS} = options ?? {};

    const inner = async (prevSize: number | null, prevCount: number, prevStableCount: number): Promise<void> => {
        const currentCount = prevCount + 1;

        if (currentCount >= Math.ceil(TIMEOUT_MS / CHECK_INTERVAL_MS)) {
            return;
        }

        const html = await this.$('body').getHTML();
        const size = html.length;
        const isEqual = prevSize === null || prevSize === size;

        const currentStableCount = isEqual ? prevStableCount + 1 : 0;

        if (currentStableCount >= minStableIterations) {
            return;
        }

        await this.pause(CHECK_INTERVAL_MS);
        return inner(size, currentCount, currentStableCount);
    };

    await inner(null, 0, 0);
}

export type WaitUntilRendered = typeof waitUntilRendered;

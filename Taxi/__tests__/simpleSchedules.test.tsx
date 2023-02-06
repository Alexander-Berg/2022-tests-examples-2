import moment from 'moment-timezone';

import {SchedulePreviewProps} from 'components/SchedulePreview';
import dates from 'utils/dates';

import {
    SCHEDULE_PREVIEW_DATA_1,
    SCHEDULE_PREVIEW_DATA_2,
    SCHEDULE_PREVIEW_DATA_3,
    SCHEDULE_PREVIEW_DATA_4,
} from './mock/simple.mock';
import {
    DATA_CY,
    mockUseSchedulePreview,
    getMarkedPreviewItems,
    renderBaseSchedule,
} from './utils';

jest.mock('../../../components/SchedulePreview/queries/useSchedulePreview');
jest.mock('../../../utils/queries/schedules/useCheckDomainIsUnderAudit');

describe('Отображение превью графика / Простые графики', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Отображение превью без смещения', () => {
        test('Отображается график 2/2 id-2 на 30 дней', async () => {
            mockUseSchedulePreview.mockImplementation(() => {
                return SCHEDULE_PREVIEW_DATA_1;
            });

            const props: SchedulePreviewProps = {
                offset: 0,
                startDate: moment('07.04.2022', dates.format.DATE_DDMMYYYY),
                scheduleType: 2,
            };
            const {item: foundItem} = renderBaseSchedule(props);

            expect(foundItem).toBeDefined();

            // дальше мы можем использовать foundItem как проверенный, иначе тест упадёт
            expect(foundItem!.getAttribute('data-cy')).toEqual(DATA_CY.WRAPPER);
            // длина массива на выходе из ручки
            expect(foundItem!.children).toHaveLength(31);

            const apiActiveSequential = SCHEDULE_PREVIEW_DATA_1.map(({isActive}) => {
                return isActive;
            });

            expect(getMarkedPreviewItems(foundItem!.children))
                .toStrictEqual(apiActiveSequential);
        });

        test('Отображается график 2/5 (раб. пн, вт) id-388 на 30 дней', async () => {
            mockUseSchedulePreview.mockImplementation(() => {
                return SCHEDULE_PREVIEW_DATA_2;
            });

            const props: SchedulePreviewProps = {
                // в этом кейсе нас не интересует смещение, потому оно не работает на такие графики
                offset: 129,
                startDate: moment('07.04.2022', dates.format.DATE_DDMMYYYY),
                scheduleType: 388,
            };
            const {item: foundItem} = renderBaseSchedule(props);

            expect(foundItem).toBeDefined();

            // дальше мы можем использовать foundItem как проверенный, иначе тест упадёт
            expect(foundItem!.getAttribute('data-cy')).toEqual(DATA_CY.WRAPPER);
            // длина массива на выходе из ручки
            expect(foundItem!.children).toHaveLength(31);

            const apiActiveSequential = SCHEDULE_PREVIEW_DATA_2.map(({isActive}) => {
                return isActive;
            });

            expect(getMarkedPreviewItems(foundItem!.children))
                .toStrictEqual(apiActiveSequential);
        });
    });

    describe('Отображение превью со смещением', () => {
        test('Отображается график 3/2 id-28 со смещением 3 на 30 дней', async () => {
            mockUseSchedulePreview.mockImplementation(() => {
                return SCHEDULE_PREVIEW_DATA_3;
            });

            const props: SchedulePreviewProps = {
                offset: 2,
                startDate: moment('07.04.2022', dates.format.DATE_DDMMYYYY),
                scheduleType: 28,
            };
            const {item: foundItem} = renderBaseSchedule(props);

            expect(foundItem).toBeDefined();

            // дальше мы можем использовать foundItem как проверенный, иначе тест упадёт
            expect(foundItem!.getAttribute('data-cy')).toEqual(DATA_CY.WRAPPER);
            // длина массива на выходе из ручки
            expect(foundItem!.children).toHaveLength(31);

            const apiActiveSequential = SCHEDULE_PREVIEW_DATA_3.map(({isActive}) => {
                return isActive;
            });

            expect(getMarkedPreviewItems(foundItem!.children))
                .toStrictEqual(apiActiveSequential);
        });

        test('Отображается график 3/2 id-28 со смещением 5 на 30 дней', async () => {
            mockUseSchedulePreview.mockImplementation(() => {
                return SCHEDULE_PREVIEW_DATA_4;
            });

            const props: SchedulePreviewProps = {
                // в этом кейсе нас не интересует смещение, потому оно не работает на такие графики
                offset: 4,
                startDate: moment('07.04.2022', dates.format.DATE_DDMMYYYY),
                scheduleType: 388,
            };
            const {item: foundItem} = renderBaseSchedule(props);

            expect(foundItem).toBeDefined();

            // дальше мы можем использовать foundItem как проверенный, иначе тест упадёт
            expect(foundItem!.getAttribute('data-cy')).toEqual(DATA_CY.WRAPPER);
            // длина массива на выходе из ручки
            expect(foundItem!.children).toHaveLength(31);

            const apiActiveSequential = SCHEDULE_PREVIEW_DATA_4.map(({isActive}) => {
                return isActive;
            });

            expect(getMarkedPreviewItems(foundItem!.children))
                .toStrictEqual(apiActiveSequential);
        });
    });
});

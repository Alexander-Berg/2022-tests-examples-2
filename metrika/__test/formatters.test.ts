import { roundNumber, addThousandsSeparator } from '../formatters-utils';

import { formatInt as formatIntRaw, FormatIntOptions } from '../format-int';
import { formatFloat as formatFloatRaw, FormatFloatOptions } from '../format-float';
import { formatCurrency as formatCurrencyRaw, FormatCurrencyOptions } from '../format-currency';
import { formatDate as formatDateRaw } from '../format-date';
import { formatTime as formatTimeRaw } from '../format-time';
import { formatPeriod as formatPeriodRaw, FormatPeriodOptions } from '../format-period';

import { Lang } from '@shared/i18n/lang';
import { Currency } from '@shared/analytics-dto/common/currency';
import { Period } from '@shared/analytics-dto/common/period';
import { DateDto } from '@shared/analytics-dto/common/date';

describe('formatter', () => {
    describe('numbers-processing', () => {
        it('should round numbers', () => {
            expect(roundNumber(1.005, 2)).toEqual(1.01);
            expect(roundNumber(1.0049, 2)).toEqual(1);
            expect(roundNumber(1.2349, 3)).toEqual(1.235);
            expect(roundNumber(1.2349, 4)).toEqual(1.2349);
        });

        it('should separate thousands', () => {
            expect(addThousandsSeparator(900, ' ')).toEqual('900');
            expect(addThousandsSeparator(1000, ' ')).toEqual('1 000');
            expect(addThousandsSeparator(42000, ' ')).toEqual('42 000');
            expect(addThousandsSeparator(142000, ' ')).toEqual('142 000');
            expect(addThousandsSeparator(32168000, ' ')).toEqual('32 168 000');
        });
    });

    describe('formatInt', () => {
        const formatInt = (n: number | string, options: FormatIntOptions = {}): string =>
            formatIntRaw(n, Lang.Ru, options);

        it('should handle incorrect value', () => {
            expect(formatInt(0.01)).toEqual('0');
            expect(formatInt(3.14)).toEqual('3');
            expect(formatInt(NaN)).toEqual('NaN');
            expect(formatInt(Infinity)).toEqual('NaN');
            expect(formatInt(0b1111)).toEqual('15');
            expect(formatInt(0o77)).toEqual('63');
            expect(formatInt(0xff)).toEqual('255');
            expect(formatInt(-1000)).toEqual('-1 000');
            expect(formatInt(1e15, { collapseThousands: true })).toEqual('1e+15');
        });

        it('should use thousands separation', () => {
            expect(formatInt(0)).toEqual('0');
            expect(formatInt(100)).toEqual('100');
            expect(formatInt(1_000)).toEqual('1 000');
            expect(formatInt(1_0000)).toEqual('10 000');
            expect(formatInt(100_000)).toEqual('100 000');
            expect(formatInt(1_000_000)).toEqual('1 000 000');
        });

        it('should collapse thousands', () => {
            expect(formatInt(1, { collapseThousands: true })).toEqual('1');
            expect(formatInt(1000, { collapseThousands: true })).toEqual('1 000');
            expect(formatInt(9999, { collapseThousands: true })).toEqual('9 999');
            expect(formatInt(10_000, { collapseThousands: true })).toEqual('10k');
            expect(formatInt(42_000, { collapseThousands: true })).toEqual('42k');
            expect(formatInt(142_000, { collapseThousands: true })).toEqual('142k');
            expect(formatInt(1_000_000, { collapseThousands: true })).toEqual('1M');
            expect(formatInt(1_000_000_000, { collapseThousands: true })).toEqual('1B');
            expect(formatInt(1_000_000_000_000, { collapseThousands: true })).toEqual('1T');
        });

        it('should use localized abbreviations', () => {
            expect(
                formatInt(100_000, {
                    collapseThousands: true,
                    useLocalizedAbbreviations: true,
                })
            ).toEqual('100 тыс');

            expect(
                formatInt(1_000_000, {
                    collapseThousands: true,
                    useLocalizedAbbreviations: true,
                })
            ).toEqual('1 млн');

            expect(
                formatInt(1_000_000_000, {
                    collapseThousands: true,
                    useLocalizedAbbreviations: true,
                })
            ).toEqual('1 млрд');

            expect(
                formatInt(1_000_000_000_000, {
                    collapseThousands: true,
                    useLocalizedAbbreviations: true,
                })
            ).toEqual('1 трлн');
        });

        it('should collapse with different threshold', () => {
            expect(formatInt(1000, { collapseThousands: true, startCollapsingFrom: 1000 })).toEqual('1k');
            expect(formatInt(1500, { collapseThousands: true, startCollapsingFrom: 1000 })).toEqual('2k');
            expect(formatInt(654321, { collapseThousands: true, startCollapsingFrom: 1000000 })).toEqual('654 321');
            expect(formatInt(1000000, { collapseThousands: true, startCollapsingFrom: 1000000 })).toEqual('1M');
        });

        it('should collapse thousands with rounding', () => {
            expect(formatInt(10_400, { collapseThousands: true })).toEqual('10k');
            expect(formatInt(10_440, { collapseThousands: true })).toEqual('10k');
            expect(formatInt(10_450, { collapseThousands: true })).toEqual('10k');
            expect(formatInt(10_500, { collapseThousands: true })).toEqual('11k');
            expect(formatInt(10_540, { collapseThousands: true })).toEqual('11k');
            expect(formatInt(10_550, { collapseThousands: true })).toEqual('11k');
            expect(formatInt(1_400_000, { collapseThousands: true })).toEqual('1,4M');
            expect(formatInt(1_440_000, { collapseThousands: true })).toEqual('1,4M');
            expect(formatInt(1_450_000, { collapseThousands: true })).toEqual('1,5M');
            expect(formatInt(1_500_000, { collapseThousands: true })).toEqual('1,5M');
            expect(formatInt(1_540_000, { collapseThousands: true })).toEqual('1,5M');
            expect(formatInt(1_560_000, { collapseThousands: true })).toEqual('1,6M');
            expect(formatInt(1_400_000_000, { collapseThousands: true })).toEqual('1,4B');
            expect(formatInt(1_500_000_000, { collapseThousands: true })).toEqual('1,5B');
            expect(formatInt(1_400_000_000_000, { collapseThousands: true })).toEqual('1,4T');
            expect(formatInt(1_500_000_000_000, { collapseThousands: true })).toEqual('1,5T');
        });

        it('should use i18n', () => {
            const formatIntEN = (n: number | string, options: FormatIntOptions = {}): string =>
                formatIntRaw(n, Lang.En, options);

            expect(formatIntEN(1_200_000)).toEqual('1,200,000');
            expect(formatIntEN(1_200_000, { collapseThousands: true })).toEqual('1.2M');
        });
    });

    describe('formatFloat', () => {
        const formatFloat = (n: number | string, options: FormatFloatOptions = {}): string =>
            formatFloatRaw(n, Lang.Ru, options);

        it('should handle incorrect value', () => {
            expect(formatFloat(NaN)).toEqual('NaN');
            expect(formatFloat(Infinity)).toEqual('Infinity');
            expect(formatFloat(0b1111)).toEqual('15');
            expect(formatFloat(0o77)).toEqual('63');
            expect(formatFloat(0xff)).toEqual('255');
        });

        it('should arrange boundaries', () => {
            expect(formatFloat(0.01)).toEqual('0,01');
            expect(formatFloat(0.009)).toEqual('< 0,01');
            expect(formatFloat(1e14)).toEqual('100 000 000 000 000');
            expect(formatFloat(1e15)).toEqual('1e+15');
        });

        it('should set decimal places', () => {
            expect(formatFloat(1.2345)).toEqual('1,23');
            expect(formatFloat(1.2345, { decimalPlaces: 4 })).toEqual('1,2345');
            expect(formatFloat(1.2345, { decimalPlaces: 0 })).toEqual('1');
            expect(formatFloat(1, { decimalPlaces: 3 })).toEqual('1');
        });

        it('should show trailing zeros', () => {
            expect(formatFloat(0.1)).toEqual('0,1');
            expect(formatFloat(0.1, { trailingZeros: true })).toEqual('0,10');
            expect(formatFloat(0.1, { decimalPlaces: 4, trailingZeros: true })).toEqual('0,1000');
            expect(formatFloat(1, { decimalPlaces: 4, trailingZeros: true })).toEqual('1,0000');
            expect(formatFloat(1.1, { decimalPlaces: 0, trailingZeros: true })).toEqual('1');
        });

        it('should show percent', () => {
            expect(formatFloat(10.3, { isPercent: true })).toEqual('10,3 %');
            expect(formatFloat(10.3, { isPercent: true, trailingZeros: true })).toEqual('10,30 %');
        });

        it('should round numbers', () => {
            expect(formatFloat(10.378, { isPercent: true })).toEqual('10,38 %');
            expect(formatFloat(10.978, { isPercent: true, decimalPlaces: 0 })).toEqual('11 %');
            expect(formatFloat(10.978, { isPercent: true, decimalPlaces: 1 })).toEqual('11 %');
            expect(formatFloat(10.878, { isPercent: true, decimalPlaces: 1 })).toEqual('10,9 %');
        });

        it('should use i18n', () => {
            const formatFloatEN = (n: number | string, options: FormatFloatOptions = {}): string =>
                formatFloatRaw(n, Lang.En, options);

            expect(formatFloatEN(0.009)).toEqual('< 0.01');
            expect(formatFloatEN(100500.04)).toEqual('100,500.04');
        });
    });

    describe('formatCurrency', () => {
        const formatCurrency = (n: number | string, options: FormatCurrencyOptions = {}): string =>
            formatCurrencyRaw(n, Lang.Ru, options);

        it('should show currency', () => {
            expect(formatCurrency(10000.348, { currency: Currency.Rub })).toEqual('10 000,35 ₽');

            expect(formatCurrency(10000, { currency: Currency.Rub })).toEqual('10 000,00 ₽');
            expect(formatCurrency(10000, { currency: Currency.Usd })).toEqual('$ 10 000,00');
            expect(formatCurrency(10000, { currency: Currency.Eur })).toEqual('10 000,00 €');
            expect(formatCurrency(10000, { currency: 'AED' })).toEqual('10 000,00 AED');
            expect(formatCurrency(10000, { currency: 'GBP' })).toEqual('10 000,00 GBP');
        });
    });

    describe('formatDate', () => {
        const date = new Date('Sep 23 1997');

        it('should format show default date', () => {
            expect(formatDateRaw(date, Lang.Ru, {})).toEqual('23.09.97');
            expect(formatDateRaw(date, Lang.En, {})).toEqual('09/23/97');
        });

        it('should format date with custom template', () => {
            const format = {
                ru: 'dd LLL yyyy',
                en: 'LLL dd, yyyy',
            };

            expect(formatDateRaw(date, Lang.Ru, { format })).toEqual('23 сен 1997');
            expect(formatDateRaw(date, Lang.En, { format })).toEqual('Sep 23, 1997');
        });
    });

    describe('formatTime', () => {
        const h = 3600;
        const m = 60;
        const formatTime = (seconds: number | string): string => formatTimeRaw(seconds);

        it('should format time', () => {
            expect(formatTime(h)).toEqual('1:00:00');
            expect(formatTime(m)).toEqual('1:00');
            expect(formatTime(0)).toEqual('0:00');
            expect(formatTime(16 * h)).toEqual('16:00:00');
            expect(formatTime(32 * m)).toEqual('32:00');
            expect(formatTime(16 * h + 32 * m)).toEqual('16:32:00');
            expect(formatTime(16 * h + 32 * m + 8)).toEqual('16:32:08');
            expect(formatTime(16 * h + 8)).toEqual('16:00:08');
        });
    });

    describe('formatPeriod', () => {
        const formatPeriod = (period: Period, options: FormatPeriodOptions = {}): string =>
            formatPeriodRaw(period, Lang.Ru, options);

        Date.now = jest.fn(() => 950475600000); // Feb 14 2000

        it('should format same period dates', () => {
            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Feb 10 2000')),
                        to: DateDto.fromDate(new Date('Feb 10 2000')),
                    })
                )
            ).toEqual('10 фев');

            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Feb 10 1999')),
                        to: DateDto.fromDate(new Date('Feb 10 1999')),
                    })
                )
            ).toEqual('10 фев 1999');
        });

        it('shoud format range of dates', () => {
            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Feb 3 2000')),
                        to: DateDto.fromDate(new Date('Feb 10 2000')),
                    })
                )
            ).toEqual('3 — 10 фев');

            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Jan 3 2000')),
                        to: DateDto.fromDate(new Date('Feb 10 2000')),
                    })
                )
            ).toEqual('3 янв — 10 фев');

            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Feb 3 1999')),
                        to: DateDto.fromDate(new Date('Feb 10 1999')),
                    })
                )
            ).toEqual('3 — 10 фев 1999');

            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Jan 3 1999')),
                        to: DateDto.fromDate(new Date('Feb 10 1999')),
                    })
                )
            ).toEqual('3 янв — 10 фев 1999');

            expect(
                formatPeriod(
                    new Period({
                        from: DateDto.fromDate(new Date('Jan 3 1999')),
                        to: DateDto.fromDate(new Date('Feb 10 2000')),
                    })
                )
            ).toEqual('3 янв 1999 — 10 фев 2000');
        });
    });
});

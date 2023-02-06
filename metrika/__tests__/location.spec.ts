import * as chai from 'chai';
import { isYandexDomain, isYandexOwnerDomain } from '../location';

describe('Location', () => {
    const createWin = ({
        hostname,
        href,
    }: {
        hostname: string;
        href: string;
    }) =>
        ({
            location: {
                hostname,
                href,
            },
        } as any);

    type TestCase = {
        hostname: string;
        href: string;
        isValid: boolean;
    };
    type RawTestCase = Omit<TestCase, 'href'>;

    const randomDomian = () => Math.random().toString().slice(2);
    const createCases = ({
        domain,
        tld,
        withDomains,
        withTlds,
        isValid = true,
        prependDomain = true,
    }: {
        domain?: string;
        tld?: string;
        withDomains?: string[];
        withTlds?: string[];
        isValid?: boolean;
        prependDomain?: boolean;
    } = {}): RawTestCase[] => {
        const cases: RawTestCase[] = [];

        if (!domain && !tld) {
            return [];
        }

        if (domain) {
            cases.push({
                hostname: domain + (tld ? `.${tld}` : ''),
                isValid,
            });
        }

        if (domain && withTlds) {
            withTlds.forEach((extraTld) => {
                cases.push({
                    hostname: `${domain}.${extraTld}`,
                    isValid,
                });
            });
        }

        if (tld && withDomains) {
            withDomains.forEach((extraDomain) => {
                cases.push({
                    hostname: `${extraDomain}.${tld}`,
                    isValid,
                });
            });
        }

        if (prependDomain) {
            cases.push(
                ...cases.map((val) => ({
                    hostname: [
                        randomDomian(),
                        randomDomian(),
                        val.hostname,
                    ].join('.'),
                    isValid: val.isValid,
                })),
            );
        }

        return cases;
    };
    const test = (
        fn: (...args: any[]) => any,
        ...testCases: RawTestCase[][]
    ) => {
        testCases
            .reduce((acc, val) => {
                return [...acc, ...val];
            }, [])
            .map(({ hostname, isValid }) => ({
                hostname,
                isValid,
                href: hostname.split('').reverse().join(''),
            }))
            .forEach(({ hostname, href, isValid }) => {
                chai.expect(
                    fn(createWin({ hostname, href })),
                    `Failed check for ${hostname}`,
                ).to.eq(isValid);
            });
    };

    it('isYandexDomain', () => {
        test(
            isYandexDomain,
            createCases({
                domain: 'yandex',
                tld: 'ru',
            }),
        );
    });

    it('isYandexOwnerDomain', () => {
        test(
            isYandexOwnerDomain,
            createCases({
                domain: 'yandex',
                tld: 'com',
                withTlds: ['ru', 'sdfsd'],
            }),
            createCases({
                domain: 'yandex-team',
                tld: 'com',
                withTlds: ['ru', 'sdfsd'],
            }),
            createCases({
                tld: 'ru',
                withDomains: ['auto', 'kinopoisk', 'beru', 'bringly'],
            }),
            createCases({
                domain: 'yango',
                tld: 'com',
            }),
            createCases({
                domain: 'neya',
                tld: 'ru',
                withTlds: ['cc'],
                isValid: false,
            }),
            createCases({
                domain: 'ya',
                tld: 'ru',
                withTlds: ['cc'],
            }),
            createCases({
                domain: 'yadi',
                tld: 'sk',
            }),
            createCases({
                domain: 'yastatic',
                tld: 'net',
            }),
            createCases({
                domain: '.yandex',
            }),
            createCases({
                domain: 'turbopages',
                tld: 'org',
            }),
            createCases({
                domain: 'turbo',
                tld: 'site',
            }),
            createCases({
                domain: 'sdfsdfsd',
                tld: 'sdfsdf',
                isValid: false,
            }),
        );
    });
});

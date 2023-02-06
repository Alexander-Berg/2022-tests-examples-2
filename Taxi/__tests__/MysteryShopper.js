import got from 'got';
import {HttpError} from '_common/server/errors';
import {MysteryShopper} from '../MysteryShopper';

jest.mock('got');

describe('MysterShopper', () => {
    let model;

    beforeEach(() => {
        model = new MysteryShopper({
            token: 'token',
            proxy: {
                url: 'proxy_url'
            }
        });
    });

    afterAll(() => {
        jest.restoreAllMocks();
    });

    it('Should be thrown an exception if config is not passed', () => {
        expect(() => {
            // eslint-disable-next-line
            new MysteryShopper();
        }).toThrow(HttpError);
    });

    it('Should be correct parse response', async () => {
        // eslint-disable-next-line
        const body = `{"question_code": "polite", "value": 1}\n{"question_code": "pdd", "value": 0}\n`;
        const trailers = {'x-yt-response-code': '0'};

        got.get.mockResolvedValue({body, trailers});

        const questions = await model.findById('id');
        expect(questions).toEqual({polite: 1, pdd: 0});
    });

    it('Should be correct group questions', async () => {
        const questions = {polite: 1, pdd: 0, driving_style: 1};
        const groups = {
            driver: ['polite', 'pdd'],
            ride: ['driving_style']
        };
        const expected = [
            {
                name: 'driver',
                questions: [
                    {
                        name: 'polite',
                        value: questions.polite
                    },
                    {
                        name: 'pdd',
                        value: questions.pdd
                    }
                ]
            },
            {
                name: 'ride',
                questions: [
                    {
                        name: 'driving_style',
                        value: questions.driving_style
                    }
                ]
            }
        ];
        expect(model.toGroup(questions, groups)).toEqual(expected);
    });

    it('Should be correct group empty groups', async () => {
        const questions = {polite: 1, pdd: 0};
        const groups = {
            driver: ['polite', 'pdd'],
            ride: ['driving_style']
        };
        const expected = [
            {
                name: 'driver',
                questions: [
                    {
                        name: 'polite',
                        value: questions.polite
                    },
                    {
                        name: 'pdd',
                        value: questions.pdd
                    }
                ]
            }
        ];
        expect(model.toGroup(questions, groups)).toEqual(expected);
    });

    it('Should be correct group empty groups and empty questions', async () => {
        const questions = {};
        const groups = {};
        const expected = [];
        expect(model.toGroup(questions, groups)).toEqual(expected);
    });
});

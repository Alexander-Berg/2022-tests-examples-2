import * as extracted from '../toggle.js';

describe('Morda.Toggle', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            setState: jest.fn(),
            elements: [
                {
                    getBoundingClientRect() {
                        return {
                            height: 100
                        };
                    }
                },
                {
                    getBoundingClientRect() {
                        return {
                            height: 200
                        };
                    }
                },
                {
                    getBoundingClientRect() {
                        return {
                            height: 300
                        };
                    }
                }
            ],
            listOpened: false,
            state: {},
            props: {
                items: [1, 2, 3],
                alwaysShown: 1,
                margin: 0
            }
        };
    });
    describe('setHeightAsync', () => {
        it('should call setState', () => {
            obj.elements = [];

            jest.useFakeTimers();
            extracted.setHeightAsync.call(obj);
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                height: 0
            });
        });
    });
    describe('shouldComponentUpdate', () => {
        it('should return true', () => {
            expect(extracted.shouldComponentUpdate.call(obj, {})).toBeTruthy();
        });
    });
    describe('getHeight', () => {
        it('should return 0', () => {
            obj.elements = [];

            expect(extracted.getHeight.call(obj)).toBe(0);
        });
        test('if listOpened is true', () => {
            const value = obj.elements.reduce((acc, cur) => {
                acc += cur.getBoundingClientRect().height;

                return acc;
            }, 0);

            obj.listOpened = true;

            expect(extracted.getHeight.call(obj)).toBe(value);
        });
        test('if listOpened is false', () => {
            const value = obj.elements[0].getBoundingClientRect().height;

            expect(extracted.getHeight.call(obj)).toBe(value);
        });
    });
    describe('toggleList', () => {
        it('should call setState and toggle listOpened prop', () => {
            const listOpened = obj.listOpened;

            obj.elements = [];

            extracted.toggleList.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                height: 0
            });
            expect(obj.listOpened).not.toBe(listOpened);
        });
    });
});

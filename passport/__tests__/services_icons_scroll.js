import * as extracted from '../services_icons_scroll.js';

describe('Registration.Mobile.Components.ServicesIconsScroll', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            firstIcon: {
                clientWidth: 100
            },
            refs: {
                scroller: {
                    scrollLeft: 200,
                    addEventListener: jest.fn(),
                    attachEvent: jest.fn()
                }
            },
            props: {
                services: [1, 2, 3, 4, 5, 6]
            }
        };
        obj.setState = jest.fn((any) => {
            obj.state = Object.assign({}, obj.state, typeof any === 'function' ? any(obj.state) : any);
        });
    });

    describe('addListenerIfNeeded', () => {
        afterEach(() => {
            obj.refs.scroller.addEventListener.mockClear();
            obj.refs.scroller.attachEvent.mockClear();
        });

        it('shouldnt call querySelector', () => {
            const querySelector = jest.spyOn(global.document, 'querySelector');

            obj.props.services = [];

            extracted.addListenerIfNeeded.call(obj);
            expect(querySelector).toHaveBeenCalledTimes(0);

            querySelector.mockRestore();
        });
        it('should call querySelector', () => {
            const querySelector = jest.spyOn(global.document, 'querySelector');

            extracted.addListenerIfNeeded.call(obj);
            expect(querySelector).toHaveBeenCalledTimes(1);
            expect(querySelector).toHaveBeenCalledWith('.scroll__icon');

            querySelector.mockRestore();
        });
        it('should call addEventListener', () => {
            extracted.addListenerIfNeeded.call(obj);
            expect(obj.refs.scroller.addEventListener).toHaveBeenCalledTimes(1);
        });
        it('should call attachEvent', () => {
            const addEventListener = window.addEventListener;

            window.addEventListener = null;

            extracted.addListenerIfNeeded.call(obj);
            expect(obj.refs.scroller.attachEvent).toHaveBeenCalledTimes(1);
            window.addEventListener = addEventListener;
        });
    });
    describe('handleScroll', () => {
        it('shouldnt call setState', () => {
            obj.props.services = [];

            extracted.handleScroll.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(0);
        });
        it('should call setState', () => {
            const innerWidth = window.innerWidth;

            extracted.handleScroll.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({scales: [0.4, 0.4, 0.4, 0.4, 0.541015625, 0.736328125]});

            obj.setState.mockClear();
            window.innerWidth = 0;
            obj.firstIcon.offsetWidth = 100;

            extracted.handleScroll.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({scales: [0.4, 0.4, 0.4, 0.4, 0.4, 0.4]});

            window.innerWidth = innerWidth;
        });
    });
});

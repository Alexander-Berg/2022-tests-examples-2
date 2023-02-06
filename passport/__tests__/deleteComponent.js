import React from 'react';
import {shallow} from 'enzyme';
import DeleteComponent from '../deleteComponent';
import DeleteForm from '../deleteForm.jsx';
import DeleteWarning from '../deleteWarning.jsx';
import {Modal} from '@components/Modal';

describe('DeleteComponent', () => {
    it('should render special text for social user', () => {
        const props = {
            isMobile: false,
            deleteAccount: {
                isModalOpened: false,
                isSocialchik: true,
                isPddAdmin: false
            },
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeleteComponent {...props} />);

        expect(wrapper.find('.social-user__text').length).toBe(1);
    });

    it('should render special text for pddAdmin user', () => {
        const props = {
            isMobile: false,
            deleteAccount: {
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: true
            },
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeleteComponent {...props} />);

        expect(wrapper.find('.pdd-admin__text').length).toBe(1);
    });

    it('should render deleteForm for normal user', () => {
        const props = {
            isMobile: false,
            deleteAccount: {
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                subscribedTo: {
                    mainList: [],
                    secondaryList: []
                }
            },
            dispatch: jest.fn(),
            isTablet: false
        };
        const wrapper = shallow(<DeleteComponent {...props} />);

        expect(wrapper.find(DeleteForm).length).toBe(1);
    });

    it('should render Modal component if is Mobile is false', () => {
        const props = {
            isMobile: false,
            deleteAccount: {
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                subscribedTo: {
                    mainList: [],
                    secondaryList: []
                }
            },
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeleteComponent {...props} />);

        expect(wrapper.find(Modal).length).toBe(1);
    });

    it('should not render Modal component if is Mobile is true', () => {
        const props = {
            isMobile: true,
            deleteAccount: {
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                subscribedTo: {
                    mainList: [],
                    secondaryList: []
                }
            },
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeleteComponent {...props} />);

        expect(wrapper.find(Modal).length).toBe(0);
    });

    it('should render DeleteWarning component if isModalOpened is true', () => {
        const props = {
            isMobile: false,
            deleteAccount: {
                isModalOpened: true,
                isSocialchik: false,
                isPddAdmin: false,
                subscribedTo: {
                    mainList: [],
                    secondaryList: []
                }
            },
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeleteComponent {...props} />);

        expect(wrapper.find(DeleteWarning).length).toBe(1);
    });
});

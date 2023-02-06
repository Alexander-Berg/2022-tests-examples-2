// tslint:disable:max-line-length
import {shallow} from 'enzyme';
import React from 'react';

import config from '_config';
import {DraftSidebarProps} from '_libs/drafts/components/types';
import {DraftModes} from '_types/common/drafts';
import {Environments} from '_types/common/infrastructure';

import {Props} from '../types';

describe('EndpointsSidebar', () => {
    const props = {
        model: {},
        endpoint: {},
        hasExistedDraft: false
    } as Props;

    afterEach(() => {
        jest.resetModules();
    });

    describe('production', () => {
        beforeEach(() => {
            jest.doMock('_config', () => ({
                ...config,
                env: Environments.Production
            }));
        });

        test('Состояние withoutDraft по умолчанию равно false', async () => {
            const EndpointsSidebar = await import('../EndpointsSidebar').then(module => module.default);
            const component = shallow(<EndpointsSidebar {...props} />);
            const withoutDraft = component.state('withoutDraft');

            expect(withoutDraft).toBeFalsy();
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения', async () => {
            const module = await import('../EndpointsSidebar');
            const EndpointsSidebar = module.default;
            const {toStableButton} = module;
            const component = shallow(<EndpointsSidebar {...props} mode={DraftModes.Edit} />);

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toStableButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });

        test('Изменение withoutDraft не влияет на установленные хендлеры кнопки сохранения', async () => {
            const module = await import('../EndpointsSidebar');
            const EndpointsSidebar = module.default;
            const {toStableButton} = module;
            const component = shallow(<EndpointsSidebar {...props} mode={DraftModes.Edit} />);

            component.setState({withoutDraft: true});

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toStableButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });
    });

    describe('development', () => {
        beforeEach(() => {
            jest.doMock('_config', () => ({
                ...config,
                env: Environments.Development
            }));
        });

        test('Состояние withoutDraft по умолчанию равно true', async () => {
            const EndpointsSidebar = await import('../EndpointsSidebar').then(module => module.default);
            const component = shallow(<EndpointsSidebar {...props} />);
            const withoutDraft = component.state('withoutDraft');

            expect(withoutDraft).toBeTruthy();
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения', async () => {
            const module = await import('../EndpointsSidebar');
            const EndpointsSidebar = module.default;
            const {unsafeCreateOrUpdateButton} = module;
            const component = shallow(<EndpointsSidebar {...props} mode={DraftModes.Edit} />);

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...unsafeCreateOrUpdateButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения при изменении withoutDraft для включенного эндпоинта', async () => {
            const model = {
                ...props.model,
                stable: {
                    ...props.model.stable,
                    enabled: true
                }
            };

            const module = await import('../EndpointsSidebar');
            const EndpointsSidebar = module.default;
            const {toPrestableButton} = module;
            const component = shallow(<EndpointsSidebar {...props} model={model} mode={DraftModes.Edit} />);

            component.setState({withoutDraft: false});

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toPrestableButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения при изменении withoutDraft для выключенного эндпоинта', async () => {
            const model = {
                ...props.model,
                enpoint: {
                    ...props.endpoint,
                    stable: {
                        ...props.endpoint?.stable,
                        enabled: false
                    }
                },
                stable: {
                    ...props.model.stable,
                    enabled: false
                }
            };

            const module = await import('../EndpointsSidebar');
            const EndpointsSidebar = module.default;
            const {toStableButton} = module;
            const component = shallow(<EndpointsSidebar {...props} model={model} mode={DraftModes.Edit} />);

            component.setState({withoutDraft: false});
            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toStableButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });
    });
});

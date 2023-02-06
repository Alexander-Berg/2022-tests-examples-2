import {shallow} from 'enzyme';
import React from 'react';

import config from '_config';
import {DraftSidebarProps} from '_libs/drafts/components/types';
import {DraftModes} from '_types/common/drafts';
import {Environments} from '_types/common/infrastructure';

import {Props} from '../types';

describe('ResourceSidebar', () => {
    const props = {
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
            const ResourceSidebar = await import('../ResourceSidebar').then(module => module.default);
            const component = shallow(<ResourceSidebar {...props} />);
            const withoutDraft = component.state('withoutDraft');

            expect(withoutDraft).toBeFalsy();
        });

        test('Устанавливаются верные хендлеры на кнопку создания', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {createButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.CreateDraft} />);

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = createButton;

            expect(expected).toStrictEqual(actual);
        });

        test('Изменение withoutDraft не влияет на установленные хендлеры кнопки создания', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {createButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.CreateDraft} />);

            component.setState({withoutDraft: true});

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = createButton;

            expect(expected).toStrictEqual(actual);
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {toPrestableButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.Edit} />);

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toPrestableButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });

        test('Изменение withoutDraft не влияет на установленные хендлеры кнопки сохранения', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {toPrestableButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.Edit} />);

            component.setState({withoutDraft: true});

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toPrestableButton, disabled: false};

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
            const ResourceSidebar = await import('../ResourceSidebar').then(module => module.default);
            const component = shallow(<ResourceSidebar {...props} />);
            const withoutDraft = component.state('withoutDraft');

            expect(withoutDraft).toBeTruthy();
        });

        test('Устанавливаются верные хендлеры на кнопку создания', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {unsafeCreateOrUpdateButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.CreateDraft} />);

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = unsafeCreateOrUpdateButton;

            expect(expected).toStrictEqual(actual);
        });

        test('Устанавливаются верные хендлеры на кнопку создания при изменении withoutDraft', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {createButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.CreateDraft} />);

            component.setState({withoutDraft: false});

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = createButton;

            expect(expected).toStrictEqual(actual);
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {unsafeCreateOrUpdateButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.Edit} />);

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...unsafeCreateOrUpdateButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });

        test('Устанавливаются верные хендлеры на кнопку сохранения при изменении withoutDraft', async () => {
            const module = await import('../ResourceSidebar');
            const ResourceSidebar = module.default;
            const {toPrestableButton} = module;
            const component = shallow(<ResourceSidebar {...props} mode={DraftModes.Edit} />);

            component.setState({withoutDraft: false});

            const expectedProps = component.find('LoadableComponent').props() as DraftSidebarProps;
            const expected = expectedProps.buttons.submitCreateButton;
            const actual = {...toPrestableButton, disabled: false};

            expect(expected).toStrictEqual(actual);
        });
    });
});

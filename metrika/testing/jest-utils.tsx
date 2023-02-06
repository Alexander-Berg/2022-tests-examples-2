import { render, shallow } from 'enzyme';
import { ReactElementsList } from 'typings/react';
import { I18nFunction } from 'utils/i18n';

export function jestSnapshotRenderTest(components: ReactElementsList): void {
    Object.entries(components).forEach(([title, component]) => {
        it(title, () => {
            const tree = render(component);
            expect(tree).toMatchSnapshot();
        });
    });
}

export function jestSnapshotShallowTest(components: ReactElementsList): void {
    Object.entries(components).forEach(([title, component]) => {
        it(title, () => {
            const tree = shallow(component).dive();
            expect(tree).toMatchSnapshot();
        });
    });
}

export function jestSnapshotInternationalizedTest(
    components: ReactElementsList,
    i18n: I18nFunction,
): void {
    Object.entries(components).forEach(([title, component]) => {
        it(title, () => {
            const i18nWrapper = shallow(component);
            const children = i18nWrapper.prop('children');

            const tree = shallow(children(i18n));
            expect(tree).toMatchSnapshot();
        });
    });
}

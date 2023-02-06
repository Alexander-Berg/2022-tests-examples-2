// import * as React from 'react';
// import { shallow } from 'enzyme';
// import { ReactElementsList } from 'typings/react';
// import { jestSnapshotShallowTest } from 'testing/jest-utils';
// import ToggleExpander from './ToggleExpander';
//
// const componentsForSnapshotRenderTest: ReactElementsList = {
// 'not expanded': <ToggleExpander expanded={false} onClick={jest.fn()} />,
//
// expanded: <ToggleExpander expanded={true} onClick={jest.fn()} />,
// };
//
// describe('ToggleExpander', () => {
// describe('renders', () => {
// jestSnapshotShallowTest(componentsForSnapshotRenderTest);
// });
//
// it('calls onClick callback', () => {
// const onClick = jest.fn();
//
// const component = shallow(
// <ToggleExpander expanded={false} onClick={onClick} />,
// );
//
// component.simulate('click');
// expect(onClick).toHaveBeenCalledTimes(1);
// });
// });
//

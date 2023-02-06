// import * as React from 'react';
// import { shallow } from 'enzyme';
// import { ReactElementsList } from 'typings/react';
// import { jestSnapshotShallowTest } from 'testing/jest-utils';

// import TreeMultiselectLabel from './TreeMultiselectLabel';
// import ToggleExpander from 'components/ToggleExpander/ToggleExpander';
// import TristateCheckBox from 'components/TristateCheckBox/TristateCheckBox';

// const callback = jest.fn();

// const labelForSnapshotRenderTest: ReactElementsList = {
//     'with loading prop provided': (
//         <TreeMultiselectLabel
//             {...{
//                 loading: true,
//                 collapsed: true,
//                 checked: 'no',

//                 onCheckboxToggle: callback,
//                 onCollapserToggle: callback,
//             }}
//         >
//             Марокко
//         </TreeMultiselectLabel>
//     ),

//     'with collapsed prop provided': (
//         <TreeMultiselectLabel
//             {...{
//                 loading: false,
//                 collapsed: false,
//                 checked: 'no',

//                 onCheckboxToggle: callback,
//                 onCollapserToggle: callback,
//             }}
//         >
//             Марокко
//         </TreeMultiselectLabel>
//     ),

//     'with checked prop "yes" provided': (
//         <TreeMultiselectLabel
//             {...{
//                 loading: false,
//                 collapsed: true,
//                 checked: 'yes',

//                 onCheckboxToggle: callback,
//                 onCollapserToggle: callback,
//             }}
//         >
//             Марокко
//         </TreeMultiselectLabel>
//     ),

//     'with checked prop "indeterminate" provided': (
//         <TreeMultiselectLabel
//             {...{
//                 loading: false,
//                 collapsed: true,
//                 checked: 'indeterminate',

//                 onCheckboxToggle: callback,
//                 onCollapserToggle: callback,
//             }}
//         >
//             Марокко
//         </TreeMultiselectLabel>
//     ),
// };

// describe('TreeMultiselectLabel', () => {
//     describe('renders', () => {
//         jestSnapshotShallowTest(labelForSnapshotRenderTest);
//     });

//     it('calls onCheckboxToggle callback', () => {
//         const onCheckboxToggle = jest.fn();

//         const component = shallow(
//             <TreeMultiselectLabel
//                 {...{
//                     onCheckboxToggle,
//                     loading: false,
//                     collapsed: false,
//                     checked: 'no',
//                     onCollapserToggle: callback,
//                 }}
//             >
//                 Марокко
//             </TreeMultiselectLabel>,
//         );

//         component.find(TristateCheckBox).simulate('change');
//         expect(onCheckboxToggle).toHaveBeenCalledTimes(1);
//     });

//     it('calls onCollapserToggle callback', () => {
//         const onCollapserToggle = jest.fn();

//         const component = shallow(
//             <TreeMultiselectLabel
//                 {...{
//                     onCollapserToggle,
//                     loading: false,
//                     collapsed: false,
//                     checked: 'no',
//                     onCheckboxToggle: callback,
//                 }}
//             >
//                 Марокко
//             </TreeMultiselectLabel>,
//         );

//         component.find(ToggleExpander).simulate('click');
//         expect(onCollapserToggle).toHaveBeenCalledTimes(1);
//     });
// });

import * as React from 'react';
import { shallow } from 'enzyme';
import {
    exportStatusActive,
    exportStatusCompleted,
    exportStatusError,
    exportStatusRunning,
    exportStatusStopped,
} from 'core/modules/CloudExportEdit/strings';
import { StatusCell } from '..';

describe('StatusCell', () => {
    test('should render active text for status `ACTIVE`', () => {
        const cell = shallow(<StatusCell status={'active'} />);
        expect(cell.children().text()).toBe(exportStatusActive);
    });

    test('should render disabled text for status `STOPPED`', () => {
        const cell = shallow(<StatusCell status={'stopped'} />);
        expect(cell.children().text()).toBe(exportStatusStopped);
    });

    test('should render completed text for status `COMPLETED`', () => {
        const cell = shallow(<StatusCell status={'completed'} />);
        expect(cell.children().text()).toBe(exportStatusCompleted);
    });

    test('should render error text for status `ERROR`', () => {
        const cell = shallow(<StatusCell status={'error'} />);
        expect(cell.children().text()).toBe(exportStatusError);
    });

    test('should render running text for status `READY_FOR_EXPORT`', () => {
        const cell = shallow(<StatusCell status={'ready_for_export'} />);
        expect(cell.children().text()).toBe(exportStatusRunning);
    });
});

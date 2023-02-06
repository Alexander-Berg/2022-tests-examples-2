import * as React from 'react';
import '@testing-library/jest-dom/extend-expect';
import { render, screen, waitFor } from '@testing-library/react';
import { ExportPage } from '..';

jest.mock('core/modules/CloudExportNew/export/data');
import { fetchExport } from 'core/modules/CloudExportNew/export/data';
jest.mock('core/modules/CloudExportNew/events/data');
import { fetchEventsData } from 'core/modules/CloudExportNew/events/data';
import { TestWrapper } from 'core/modules/CloudExportNew/utils/tests';

beforeAll(() => {
    // @ts-ignore
    global.BN = jest.fn().mockReturnValue({
        get: jest.fn().mockReturnValue({ parentId: '321' }),
    });
});
afterAll(() => {
    jest.restoreAllMocks();
});
describe('ExportPage', () => {
    it('Render events loading error', async () => {
        const error = { body: { message: 'Events loading error' } };
        // @ts-ignore
        fetchEventsData.mockRejectedValue(error);

        render(
            <TestWrapper>
                <ExportPage />
            </TestWrapper>,
        );
        await waitFor(() => screen.getByText(error.body.message));

        expect(screen.getByText(error.body.message)).toBeInTheDocument();
    });
});
describe('ExportPage', () => {
    it('Render parent export loading error', async () => {
        const error = { body: { message: 'Parent export loading error' } };
        // @ts-ignore
        fetchEventsData.mockResolvedValue({});
        // @ts-ignore
        fetchExport.mockRejectedValue(error);

        render(
            <TestWrapper>
                <ExportPage />
            </TestWrapper>,
        );
        await waitFor(() => screen.getByText(error.body.message));

        expect(screen.getByText(error.body.message)).toBeInTheDocument();
    });
});

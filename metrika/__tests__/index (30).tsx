import * as React from 'react';
import { findByText, fireEvent, render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { TestWrapper } from 'core/modules/CloudExportNew/utils/tests';
import { EventTypeTabs } from '..';
import { ExportDraftProvider } from '../../DraftContext';
import { EventsProvider } from '../../EventsContext';
import { OneTimeCloudExport } from 'ajax/cloud';
import { EventsData } from 'core/modules/CloudExportNew/events/data';
import { find, head } from 'lodash';

const events: EventsData = {
    eventsTypes: [
        'clientEvents',
        'installations',
        'revenueEvents',
        'sessionsStarts',
    ],
    eventDataByType: {
        clientEvents: {
            apiKey: 'client_events',
            fields: [],
            title: 'Cобытия',
        },
        installations: {
            apiKey: 'installations',
            fields: [],
            title: 'Установки',
        },
        revenueEvents: {
            apiKey: 'revenue_events',
            fields: [],
            title: 'Revenue-события',
        },
        sessionsStarts: {
            apiKey: 'sessions_starts',
            fields: [],
            title: 'Начала сессий',
        },
    },
};

const defaultType = head(events.eventsTypes);

describe('EventTypeTabs', () => {
    it('should render draft value selected', async () => {
        const draftType: OneTimeCloudExport['meta_table_name'] =
            'revenue_events';
        const { container } = render(
            <TestWrapper>
                <ExportDraftProvider
                    value={
                        {
                            meta_table_name: draftType,
                        } as OneTimeCloudExport
                    }
                >
                    <EventsProvider value={events}>
                        <EventTypeTabs />
                    </EventsProvider>
                </ExportDraftProvider>
            </TestWrapper>,
        );

        const matchedEventInfo = find(
            events.eventDataByType,
            ({ apiKey }) => apiKey === draftType,
        );
        const el = await findByText(
            container.querySelector<HTMLElement>(
                '.radiobox__radio_checked_yes',
            )!,
            matchedEventInfo!.title,
        );
        expect(el).toBeInTheDocument();
    });

    it('should render default value selected when draft invalid', async () => {
        const draftType = 'invalid_type';
        const { container } = render(
            <TestWrapper>
                <ExportDraftProvider
                    value={
                        {
                            meta_table_name: draftType,
                        } as any
                    }
                >
                    <EventsProvider value={events}>
                        <EventTypeTabs />
                    </EventsProvider>
                </ExportDraftProvider>
            </TestWrapper>,
        );

        const el = await findByText(
            container.querySelector<HTMLElement>(
                '.radiobox__radio_checked_yes',
            )!,
            events.eventDataByType[defaultType!].title,
        );
        expect(el).toBeInTheDocument();
    });

    it('should render default value selected when no draft', async () => {
        const { container } = render(
            <TestWrapper>
                <ExportDraftProvider value={null}>
                    <EventsProvider value={events}>
                        <EventTypeTabs />
                    </EventsProvider>
                </ExportDraftProvider>
            </TestWrapper>,
        );

        const el = await findByText(
            container.querySelector<HTMLElement>(
                '.radiobox__radio_checked_yes',
            )!,
            events.eventDataByType[defaultType!].title,
        );
        expect(el).toBeInTheDocument();
    });

    it('should change selected onClick', async () => {
        const { container } = render(
            <TestWrapper>
                <ExportDraftProvider value={null}>
                    <EventsProvider value={events}>
                        <EventTypeTabs />
                    </EventsProvider>
                </ExportDraftProvider>
            </TestWrapper>,
        );
        const titleToClick =
            events.eventDataByType[events.eventsTypes[2]].title;
        fireEvent.click(await findByText(container, titleToClick));

        const el = await findByText(
            container.querySelector<HTMLElement>(
                '.radiobox__radio_checked_yes',
            )!,
            titleToClick,
        );
        expect(el).toBeInTheDocument();
    });
});

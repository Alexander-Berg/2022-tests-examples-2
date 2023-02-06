import * as React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ApplicationProvider } from 'core/modules/CloudExportNew/components/ApplicationContext';
import { ApplicationItem } from 'typings/bem';
import { Provider } from 'react-redux';
import * as ducks from '../../ducks';
import { createStoreFromDucks } from 'lib/reducktor';
import { filter } from 'lodash';

const { store } = createStoreFromDucks(
    filter(ducks, ({ key }) => Boolean(key)),
);

export const TestWrapper: React.FC = ({ children }) => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                refetchOnWindowFocus: false,
                refetchOnMount: false,
                retryOnMount: false,
            },
        },
    });

    return (
        <Provider store={store}>
            <QueryClientProvider client={queryClient}>
                <ApplicationProvider
                    value={{
                        application: { id: 123 } as ApplicationItem,
                    }}
                >
                    {children}
                </ApplicationProvider>
            </QueryClientProvider>
        </Provider>
    );
};

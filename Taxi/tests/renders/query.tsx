import React, {PropsWithChildren, ReactNode} from 'react';
import {QueryClient, QueryClientProvider} from 'react-query';

export function createQueryClient() {
    return new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    });
}

export function createQueryProvider(children: ReactNode) {
    const queryClient = createQueryClient();

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}

export function Wrapper<T>({children}: PropsWithChildren<T>) {
    const queryClient = createQueryClient();

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}

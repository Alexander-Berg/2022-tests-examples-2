import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { baseApiUrl } from '../../app/urls';
import { List } from './common';

interface ExpFlag {
    n: string;
    v: string;
}

export interface Testid {
    id: number;
    author: string;
    time_created: string;
    time_modified: string;
    title: string;
    slot: number;
    params: ExpFlag[];
    task: number;
}

export interface CreateTestid {
    client_id: string;
    testid: Omit<Testid, 'id' | 'time_created' | 'time_modified' | 'author'>;
}

interface GetTestid {
    id: number;
    client_id: string;
}

export interface UpdateTestid extends GetTestid {
    testid: Partial<CreateTestid['testid']>;
}

export type TestidsList = List<Testid>;

const testidUrl = '/testid';

export const testidApi = createApi({
    reducerPath: 'testidApi',
    baseQuery: fetchBaseQuery({
        baseUrl: baseApiUrl,
    }),
    tagTypes: ['testids'],
    endpoints: builder => ({
        getTestidsList: builder.query<TestidsList, { client_id: string; task__id: number }>({
            query: ({ client_id, task__id }) => ({
                url: `${testidUrl}/`,
                params: {
                    task__id,
                    client_id,
                },
            }),
            providesTags: ['testids'],
        }),
        getTestid: builder.query<Testid, GetTestid>({
            query: ({ id, client_id }) => ({ url: `${testidUrl}/${id}/`, params: { client_id } }),
        }),
        createTestid: builder.mutation<Testid, CreateTestid>({
            query: ({ testid, client_id }) => ({
                url: `${testidUrl}/`,
                method: 'POST',
                body: testid,
                params: { client_id },
            }),
            invalidatesTags: ['testids'],
        }),
        deleteTestid: builder.mutation<Testid, GetTestid>({
            query: ({ client_id, id }) => ({
                url: `${testidUrl}/${id}/`,
                method: 'DELETE',
                params: {
                    client_id,
                },
            }),
            invalidatesTags: ['testids'],
        }),
        updateTestid: builder.mutation<Testid, UpdateTestid>({
            query: ({ client_id, id, testid }) => ({
                url: `${testidUrl}/${id}/`,
                method: 'PATCH',
                body: testid,
                params: {
                    client_id,
                },
            }),
            invalidatesTags: ['testids'],
        }),
    }),
});

export const {
    useGetTestidsListQuery,
    useGetTestidQuery,
    useCreateTestidMutation,
    useUpdateTestidMutation,
    useDeleteTestidMutation,
} = testidApi;

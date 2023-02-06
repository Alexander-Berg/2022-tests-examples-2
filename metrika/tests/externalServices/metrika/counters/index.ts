import { advApi } from 'server/api/admetrica';
import cfg from 'yandex-cfg';
import { Request } from 'express';
import {
    CounterToSave,
    SavedCounter,
} from 'tests/externalServices/metrika/types';

const apiParams = cfg.metrikaApi;
const { counters, counter } = apiParams.endpoints;
const countersUrl = `${apiParams.serverUrl}${counters}`;
const counterUrl = `${apiParams.serverUrl}${counter}`;

type CreateCounterOptions = {
    counter: CounterToSave;
};

type CreateCounterResult = {
    counter: SavedCounter;
};

function createCounter(req: Request, options: CreateCounterOptions) {
    return advApi
        .post<CreateCounterResult>(countersUrl, {
            context: req,
            json: {
                counter: options.counter,
            },
        })
        .then(({ counter }) => ({ counter }));
}

type DeleteCounterOptions = {
    counterId: number;
};

function deleteCounter(req: Request, options: DeleteCounterOptions) {
    return advApi.delete<never>(`${counterUrl}/${options.counterId}`, {
        context: req,
    });
}

export { createCounter, deleteCounter };

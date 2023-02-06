import {
    createCounter as createCounterRequest,
    deleteCounter as deleteCounterRequest,
} from 'tests/externalServices/metrika/counters';
import { GoalToSave } from 'tests/externalServices/metrika/types';
import { bindRequest } from 'tests/utils/api';

const boundCreateCounter = bindRequest(createCounterRequest);
const boundDeleteCounter = bindRequest(deleteCounterRequest);

const createCounter = async (name: string, goals: GoalToSave[]) => {
    const { counter } = await boundCreateCounter({
        counter: {
            name,
            goals,
            site2: {
                site: name,
            },
        },
    });

    return counter;
};

const deleteCounterById = async (id: number) => {
    await boundDeleteCounter({ counterId: id });
};

export { createCounter, deleteCounterById };

import {CRUDAPI} from './CRUDAPI';
import {PipelineTest, TestsEnumerateResponse} from './types';

const ENDPOINT = 'test';

export const apiInstance = new CRUDAPI<PipelineTest, TestsEnumerateResponse>(ENDPOINT);

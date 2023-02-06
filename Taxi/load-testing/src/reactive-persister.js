/*
  Расширяем непубличные свойства, поэтому TS только мешает...
 */

import Persister from '@pollyjs/persister';

import {loadTesting} from '.';

const $storage = Symbol('storage');
const $cachedRequestIds = Symbol('cachedRequestIds');
const $newRequestIds = Symbol('newRequestIds');
let $recordingsCache = Symbol('recordingsCache');

export class ReactivePersister extends Persister {
    constructor(...args) {
        super(...args);

        this[$storage] = new Map(); // записи в памяти приложения
        this[$cachedRequestIds] = new Set();
        this[$newRequestIds] = new Set();

        const recordings = loadTesting.api.loadRecordingsCache(); // записи загруженные при старте приложения
        if (recordings) {
            this[$recordingsCache] = recordings;

            const ids = recordings.log.entries.map(({_id}) => _id);
            this[$cachedRequestIds] = new Set(ids);

            loadTesting.api.log.info(`Found ${ids.length} cached requests`);
        } else {
            $recordingsCache = undefined;
        }
    }

    static get id() {
        return 'reactive';
    }

    onFindRecording(recordingId) {
        // Единоразово копируем в память записи из файла:
        if ($recordingsCache) {
            this[$storage].set(recordingId, this[$recordingsCache]);
            this[$recordingsCache] = undefined;
            $recordingsCache = undefined;
        }

        const data = this[$storage].get(recordingId);

        loadTesting.api.log.debug(`ReactivePersister :: findRecording :: ${recordingId}`);

        return data || null;
    }

    /**
     * Вызывается из `this.persist()`
     */
    onSaveRecording(recordingId, data) {
        loadTesting.api.log.debug(`ReactivePersister :: saveRecording :: ${recordingId}`);

        // обновляем кэш в памяти
        this[$storage].set(recordingId, data);

        // обновляем постоянный кэш
        const newRequestIds = [...this[$newRequestIds]];
        this[$newRequestIds] = new Set();
        loadTesting.api.persistRecordings(data, newRequestIds);
    }

    onDeleteRecording(recordingId) {
        loadTesting.api.log.debug(`ReactivePersister :: deleteRecording :: ${recordingId}`);

        this[$storage].delete(recordingId);
    }

    /**
     * Вызывается, если запрос не нашелся в кэше
     */
    recordRequest(pollyRequest) {
        super.recordRequest(pollyRequest);

        const id = pollyRequest.id;

        if (!this[$cachedRequestIds].has(id)) {
            this[$cachedRequestIds].add(id);
            this[$newRequestIds].add(id);
            void this.persist();

            loadTesting.api.log.info(`ReactivePersister :: recordRequest :: Missed request cache "${id}"`);
        }
    }
}

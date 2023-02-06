import fs from 'fs';
import {times} from 'lodash';
import moment from 'moment';
import {addTask} from 'tests/unit/add-task';
import {In} from 'typeorm';
import {v4} from 'uuid';

import {Documents} from '@/src/entities/documents/entity';
import {generateStores, getDocumentByS3Key} from '@/src/test/test-factory';
import type {ApiRequestContext} from 'server/routes/api-handler';
import {ensureConnection} from 'service/db';
import * as s3Uploader from 'service/helper/upload-to-s3';
import * as sqs from 'service/sqs/sender';
import {CorrectDocumentType, DocumentType} from 'types/documents';

import {saveHandler} from './save';
import {uploadHandler} from './upload';

const uploadToS3 = jest.spyOn(s3Uploader, 'uploadToS3');
const sendMessage = jest.spyOn(sqs, 'sendSqsMessage');

describe('API PDF confirm handler', () => {
    it('should insert document to DB', async () => {
        uploadToS3.mockReturnValue(
            new Promise((resolve) => {
                resolve('s3KeyStub');
            })
        );

        sendMessage.mockResolvedValue(undefined);

        const stores = await generateStores(1, () => ({}));
        const taskId: number = (
            await addTask('externalId-1', stores.raw[0].id, {}, moment(new Date()).format('YYYYMMDD'))
        ).identifiers[0].id;

        const {uid} = await uploadHandler.handle({
            data: {
                file: {
                    buffer: await fs.ReadStream.from('stub content'),
                    originalname: 'file.pdf'
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        const date = new Date();

        await saveHandler.handle({
            data: {
                body: {
                    taskId,
                    files: [
                        {
                            uid,
                            type: CorrectDocumentType.ConsignmentNote,
                            number: '1',
                            date: date.toISOString(),
                            groupNumber: 1
                        }
                    ],
                    manualCheckIsRequired: false
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        const stubDocumentEntity = await getDocumentByS3Key('s3KeyStub');

        expect(uploadToS3).toBeCalled();
        expect(stubDocumentEntity?.originalDocumentImage).toBe('s3KeyStub');
        expect(stubDocumentEntity?.status).toBe('NEW');
        expect(stubDocumentEntity?.number).toBe('1');
        expect(stubDocumentEntity?.date.toISOString()).toBe(date.toISOString());
        expect(stubDocumentEntity?.type).toBe(CorrectDocumentType.ConsignmentNote);
    });

    it('should return 404 status code', async () => {
        const {uid} = await uploadHandler.handle({
            data: {
                file: {
                    buffer: await fs.ReadStream.from('stub content'),
                    originalname: 'file.pdf'
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        await expect(
            saveHandler.handle({
                data: {
                    body: {
                        taskId: 2007,
                        files: [
                            {
                                uid,
                                type: CorrectDocumentType.ConsignmentNote,
                                number: '1',
                                date: new Date().toISOString(),
                                groupNumber: 1
                            }
                        ],
                        manualCheckIsRequired: false
                    }
                },
                context: ({} as unknown) as ApiRequestContext
            })
        ).rejects.toThrow('taskId is not found');
    });

    it('should confirm only new S3 uids', async () => {
        uploadToS3.mockReturnValue(
            new Promise((resolve) => {
                resolve('s3KeyStub1');
            })
        );

        sendMessage.mockResolvedValue(undefined);

        const stores = await generateStores(1, () => ({}));
        const taskId: number = (
            await addTask('externalId-2', stores.raw[0].id, {}, moment(new Date()).format('YYYYMMDD'))
        ).identifiers[0].id;

        const {uid: duplicatedUid} = await uploadHandler.handle({
            data: {
                file: {
                    buffer: await fs.ReadStream.from('stub content'),
                    originalname: 'file.pdf'
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        await saveHandler.handle({
            data: {
                body: {
                    taskId,
                    files: [
                        {
                            uid: duplicatedUid,
                            type: CorrectDocumentType.ConsignmentNote,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 1
                        }
                    ],
                    manualCheckIsRequired: false
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        uploadToS3.mockReturnValue(
            new Promise((resolve) => {
                resolve('s3KeyStub2');
            })
        );

        const {uid: singleUid} = await uploadHandler.handle({
            data: {
                file: {
                    buffer: await fs.ReadStream.from('stub content'),
                    originalname: 'file.pdf'
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        await saveHandler.handle({
            data: {
                body: {
                    taskId,
                    files: [
                        {
                            uid: singleUid,
                            type: CorrectDocumentType.ConsignmentNote,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 1
                        },
                        {
                            uid: duplicatedUid,
                            type: CorrectDocumentType.ConsignmentNote,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 1
                        }
                    ],
                    manualCheckIsRequired: false
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        const connection = await ensureConnection();

        const duplicatedUidDocs = await connection
            .getRepository(Documents)
            .find({where: {originalDocumentImage: 's3KeyStub1'}});
        const singleUidDocs = await connection
            .getRepository(Documents)
            .find({where: {originalDocumentImage: 's3KeyStub2'}});

        expect(duplicatedUidDocs).toHaveLength(1);
        expect(singleUidDocs).toHaveLength(1);
    });

    it('should save another document with description', async () => {
        uploadToS3.mockResolvedValue(v4());
        sendMessage.mockResolvedValue(undefined);

        const stores = await generateStores(1, () => ({}));
        const taskId: number = (
            await addTask('externalId-3', stores.raw[0].id, {}, moment(new Date()).format('YYYYMMDD'))
        ).identifiers[0].id;

        const uids = (
            await Promise.all(
                times(2, async () =>
                    uploadHandler.handle({
                        data: {
                            file: {
                                buffer: await fs.ReadStream.from('stub content'),
                                originalname: 'file.pdf'
                            }
                        },
                        context: ({} as unknown) as ApiRequestContext
                    })
                )
            )
        ).map((uploadResponce) => uploadResponce.uid);

        await saveHandler.handle({
            data: {
                body: {
                    taskId,
                    files: [
                        {
                            uid: uids[0],
                            type: CorrectDocumentType.ConsignmentNote,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 1
                        },
                        {
                            uid: uids[1],
                            type: DocumentType.Another,
                            description: 'another',
                            groupNumber: 1
                        }
                    ],
                    manualCheckIsRequired: false
                }
            },
            context: ({getUser: async () => ({id: 1})} as unknown) as ApiRequestContext
        });

        const connection = await ensureConnection();

        const anotherDocument = await connection.getRepository(Documents).find({where: {uid: uids[1]}});

        expect(anotherDocument).toHaveLength(1);
        expect(anotherDocument[0].description).toBe('another');
    });

    it('should save packing list and invoice only together', async () => {
        uploadToS3.mockResolvedValue(v4());
        sendMessage.mockResolvedValue(undefined);

        const stores = await generateStores(1, () => ({}));
        const taskId: number = (
            await addTask('externalId-4', stores.raw[0].id, {}, moment(new Date()).format('YYYYMMDD'))
        ).identifiers[0].id;

        const uids = (
            await Promise.all(
                times(2, async () =>
                    uploadHandler.handle({
                        data: {
                            file: {
                                buffer: await fs.ReadStream.from('stub content'),
                                originalname: 'file.pdf'
                            }
                        },
                        context: ({getUser: async () => ({id: 1})} as unknown) as ApiRequestContext
                    })
                )
            )
        ).map((uploadResponce) => uploadResponce.uid);

        await expect(
            saveHandler.handle({
                data: {
                    body: {
                        taskId,
                        files: [
                            {
                                uid: uids[0],
                                type: CorrectDocumentType.Invoice,
                                number: '1',
                                date: new Date().toISOString(),
                                groupNumber: 1
                            }
                        ],
                        manualCheckIsRequired: false
                    }
                },
                context: ({} as unknown) as ApiRequestContext
            })
        ).rejects.toThrow();

        await expect(
            saveHandler.handle({
                data: {
                    body: {
                        taskId,
                        files: [
                            {
                                uid: uids[0],
                                type: CorrectDocumentType.PackingList,
                                number: '1',
                                date: new Date().toISOString(),
                                groupNumber: 1
                            },
                            {
                                uid: uids[1],
                                type: CorrectDocumentType.Invoice,
                                number: '1',
                                date: new Date().toISOString(),
                                groupNumber: 1
                            }
                        ],
                        manualCheckIsRequired: false
                    }
                },
                context: ({} as unknown) as ApiRequestContext
            })
        ).resolves.toBeDefined();
    });

    it('should save documents with different group numbers', async () => {
        uploadToS3.mockResolvedValue(v4());
        sendMessage.mockResolvedValue(undefined);

        const stores = await generateStores(1, () => ({}));
        const taskId: number = (
            await addTask('externalId-5', stores.raw[0].id, {}, moment(new Date()).format('YYYYMMDD'))
        ).identifiers[0].id;

        const uids = (
            await Promise.all(
                times(4, async () =>
                    uploadHandler.handle({
                        data: {
                            file: {
                                buffer: await fs.ReadStream.from('stub content'),
                                originalname: 'file.pdf'
                            }
                        },
                        context: ({} as unknown) as ApiRequestContext
                    })
                )
            )
        ).map((uploadResponce) => uploadResponce.uid);

        await saveHandler.handle({
            data: {
                body: {
                    taskId,
                    files: [
                        {
                            uid: uids[0],
                            type: CorrectDocumentType.ConsignmentNote,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 1
                        },
                        {
                            uid: uids[1],
                            type: CorrectDocumentType.UniversalTransferDocument,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 2
                        },
                        {
                            uid: uids[2],
                            type: CorrectDocumentType.Invoice,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 3
                        },
                        {
                            uid: uids[3],
                            type: CorrectDocumentType.PackingList,
                            number: '1',
                            date: new Date().toISOString(),
                            groupNumber: 3
                        }
                    ],
                    manualCheckIsRequired: false
                }
            },
            context: ({} as unknown) as ApiRequestContext
        });

        const connection = await ensureConnection();

        const documents = await connection.getRepository(Documents).find({where: {uid: In(uids)}});

        expect(documents).toHaveLength(4);
        expect(
            documents.map((document) => document.groupNumber).sort((first, second) => first - second)
        ).toStrictEqual([1, 2, 3, 3]);
    });
});

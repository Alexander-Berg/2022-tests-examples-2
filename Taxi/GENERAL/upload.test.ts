import fs from 'fs';

import type {ApiRequestContext} from 'server/routes/api-handler';
import * as s3Uploader from 'service/helper/upload-to-s3';

import {uploadHandler} from './upload';

const uploadToS3 = jest.spyOn(s3Uploader, 'uploadToS3');

describe('API PDF upload handler', () => {
    it('should return 500 status code', async () => {
        uploadToS3.mockReturnValue(
            new Promise((resolve) => {
                resolve('');
            })
        );

        await expect(
            uploadHandler.handle({
                data: {
                    file: {
                        buffer: await fs.ReadStream.from('stub content')
                    }
                },
                context: ({} as unknown) as ApiRequestContext
            })
        ).rejects.toThrow('failed to upload to S3');
    });
});

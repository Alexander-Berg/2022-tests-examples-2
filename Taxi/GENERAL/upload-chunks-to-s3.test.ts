import {uploadChunksToS3} from 'server/recognition/upload-chunks-to-s3';
import * as UploadToS3 from 'service/helper/upload-to-s3';

const uploadToS3 = jest.spyOn(UploadToS3, 'uploadToS3');

describe('upload images to s3', () => {
    it('uploadChunksToS3 should return array of keys', async () => {
        const sharedData = {
            bufferIndex: 0
        };

        uploadToS3.mockImplementation(async () => {
            ++sharedData.bufferIndex;

            return sharedData.bufferIndex.toString();
        });

        const buffers: Buffer[] = new Array(10).fill(0).map((_) => new Buffer('stubContent'));

        const keys = await uploadChunksToS3(buffers, 'root');

        expect(keys).toEqual(new Array(10).fill(0).map((_, index) => (index + 1).toString()));
    });
});

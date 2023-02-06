import {generatePngString} from 'service/seed-db/utils/generate-png';
import {ImageSize} from 'types/image';

export function generateImageBufferFromUrl(url: string, size = ImageSize.ORIGINAL) {
    const imageBase64 = generatePngString(url, size);
    const imgBuffer = Buffer.from(imageBase64, 'base64');

    return imgBuffer;
}

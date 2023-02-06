import fs from 'fs';
import os from 'os';
import path from 'path';

import buildImageUrlFromCode from 'service/seed-db/utils/build-image-url-from-code';
import {generatePngString} from 'service/seed-db/utils/generate-png';

type FileName = `${string}.${typeof EXT}`;

/**
 * @description Размер стороны изображения в пикселях (т.е. 800 x 800)
 */
const IMAGE_SIZE = 800;

/**
 * @description Расширения файла изображения (всегда .png)
 */
const EXT = 'png';

/**
 * @description Генерирует псевдослучайный файл изображения детерминированный по имени,
 * записывает на диск во временную директорию ОС, возвращает путь
 * @param name Имя файла
 * @param imageSize Размер стороны изображения в пикселях
 */
export default function createImageFile(name: FileName, imageSize: number = IMAGE_SIZE) {
    const imageBase64 = generatePngString(buildImageUrlFromCode(name), imageSize);

    const dirName = os.tmpdir();
    const pathToFile = path.join(dirName, name);
    fs.writeFileSync(pathToFile, imageBase64, {encoding: 'base64'});

    return pathToFile;
}

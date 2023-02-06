import fs from 'fs';
import * as cv from 'opencv4nodejs';

import {serviceResolve} from '@/src/lib/resolve';
import {writeFileIfDevelopment} from 'service/helper/write-file-if-development';

import {addBorderAndCrop, onceRotateMat, tableCellRects2JSON} from './opencv-utils';

describe('tableCellRects2JSON', () => {
    it('should return JSON by rects', async () => {
        const rects: cv.Rect[] = [
            new cv.Rect(0, 0, 10, 10),
            new cv.Rect(10, 0, 10, 10),
            new cv.Rect(0, 10, 10, 10),
            new cv.Rect(10, 10, 10, 10)
        ];

        const expectedJSON = [
            {
                rects: [new cv.Rect(10, 10, 10, 10), new cv.Rect(0, 10, 10, 10)],
                options: {}
            },
            {
                rects: [new cv.Rect(10, 0, 10, 10), new cv.Rect(0, 0, 10, 10)],
                options: {}
            }
        ];

        expect(await tableCellRects2JSON(rects)).toStrictEqual(expectedJSON);
    });
});

describe('rotate image', () => {
    function runTest(imgPath: string, expectedAngle: number, pathToSave: string) {
        const imgBuffer = fs.readFileSync(imgPath);
        const mat = cv.imdecode(imgBuffer);

        const rotated = onceRotateMat(mat);

        const rotatedBuffer = cv.imencode('.jpeg', rotated.rotatedMat);
        writeFileIfDevelopment(pathToSave, rotatedBuffer);

        expect(Math.abs((rotated.angle ?? 0) - expectedAngle)).toBeLessThanOrEqual(0.5);
    }

    it('just works', () => {
        runTest(
            serviceResolve('./src/service/opencv-table-recognition/rotated-samples/1/1.jpg'),
            11.3,
            serviceResolve('./src/service/opencv-table-recognition/rotated-samples/1/rotated.jpg')
        );
        runTest(
            serviceResolve('./src/service/opencv-table-recognition/rotated-samples/2/2.jpg'),
            -5,
            serviceResolve('./src/service/opencv-table-recognition/rotated-samples/2/rotated.jpg')
        );
        runTest(
            serviceResolve('./src/service/opencv-table-recognition/rotated-samples/3/3.jpg'),
            8,
            serviceResolve('./src/service/opencv-table-recognition/rotated-samples/3/rotated.jpg')
        );
    });
});

describe('crop image', () => {
    function runTest(imgPath: string, sizeAfterCrop: {w: number; h: number}, pathToSave: string) {
        const imgBuffer = fs.readFileSync(imgPath);
        const mat = cv.imdecode(imgBuffer);

        const croppedMat = addBorderAndCrop(mat).borderedImg;

        const croppedBuffer = cv.imencode('.jpeg', croppedMat);
        writeFileIfDevelopment(pathToSave, croppedBuffer);

        expect(Math.abs(croppedMat.cols - sizeAfterCrop.w)).toBeLessThanOrEqual(10);
        expect(Math.abs(croppedMat.rows - sizeAfterCrop.h)).toBeLessThanOrEqual(10);
    }

    it('just works', () => {
        runTest(
            serviceResolve('./src/service/opencv-table-recognition/cropped-samples/1/1.jpg'),
            {w: 3335, h: 1755},
            serviceResolve('./src/service/opencv-table-recognition/cropped-samples/1/cropped.jpg')
        );
        runTest(
            serviceResolve('./src/service/opencv-table-recognition/cropped-samples/2/2.jpg'),
            {w: 2850, h: 1880},
            serviceResolve('./src/service/opencv-table-recognition/cropped-samples/2/cropped.jpg')
        );
    });

    it('noisy image', () => {
        runTest(
            serviceResolve('./src/service/opencv-table-recognition/cropped-samples/3/3.jpg'),
            {w: 2125, h: 1385},
            serviceResolve('./src/service/opencv-table-recognition/cropped-samples/3/cropped.jpg')
        );
    });
});

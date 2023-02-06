import {promises as fs} from 'fs';
import kebabCase from 'lodash/kebabCase';
import path from 'path';
import type {ElementHandle, Page, ScreenshotOptions} from 'puppeteer';

import type {SaveImageSnapshotOptions} from '@/@types/tests/jest';

async function assertImage(pageOrElement: Page | ElementHandle, shapshotName: string, options?: ScreenshotOptions) {
    const shouldUpdateScreenshot = Boolean(process.env.UPDATE_SCREEN);
    const testDir = path.dirname(expect.getState().testPath);
    const shapshotDir = `${testDir}/screenshots/${shouldUpdateScreenshot ? 'expected' : 'actual'}`;
    const screen = await pageOrElement.screenshot(options);

    try {
        expect(screen).toMatchImageSnapshot({
            customSnapshotsDir: shapshotDir,
            customSnapshotIdentifier: getSnapshotIdentifier(shapshotName)
        });
    } catch (error) {
        // Сохраняем актуальный скрин для отчета
        expect(screen).toSaveImage({shapshotDir, shapshotName});
        throw error;
    }
}

interface getSnapshotIdentifierOptions {
    testPath: string;
    currentTestName: string;
}

function getSnapshotBaseIdentifier({testPath, currentTestName}: getSnapshotIdentifierOptions) {
    return kebabCase(`${path.basename(testPath)}-${currentTestName}`);
}

function getSnapshotIdentifier(name: string) {
    return (options: getSnapshotIdentifierOptions) => name + '-' + getSnapshotBaseIdentifier(options);
}

async function toSaveImage(
    this: {testPath: string; currentTestName: string},
    receivedImageBuffer: Buffer,
    {shapshotDir, shapshotName}: SaveImageSnapshotOptions
) {
    const {testPath, currentTestName} = this;
    const snapshotIdentifier = getSnapshotIdentifier(shapshotName)({testPath, currentTestName});
    const baselineSnapshotPath = path.join(shapshotDir, `${snapshotIdentifier}-snap.png`);

    await fs.writeFile(baselineSnapshotPath, receivedImageBuffer);

    return {pass: true, message: () => ''};
}

export {assertImage, getSnapshotIdentifier, toSaveImage};

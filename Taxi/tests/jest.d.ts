export interface SaveImageSnapshotOptions {
    shapshotDir: string;
    shapshotName: string;
}

declare global {
    namespace jest {
        interface Matchers<R> {
            toSaveImage(options?: SaveImageSnapshotOptions): R;
        }
    }
}

declare namespace WebdriverIO {
    import 'hermione/typings/webdriverio';

    /* eslint-disable max-len */

    interface Browser {
        findByTestId: import('./config/commands/find-by-test-id').FindByTestId;
        waitUntilRendered: import('./config/commands/wait-until-rendered').WaitUntilRendered;
        waitForTestIdSelectorInDom: import('./config/commands/wait-for-test-id-selector-presence').WaitForTestIdSelectorInDom;
        waitForTestIdSelectorNotInDom: import('./config/commands/wait-for-test-id-selector-presence').WaitForTestIdSelectorNotInDom;
        waitForTestIdSelectorVisible: import('./config/commands/wait-for-test-id-selector-presence').WaitForTestIdSelectorVisible;
        waitForTestIdSelectorNotVisible: import('./config/commands/wait-for-test-id-selector-presence').WaitForTestIdSelectorNotVisible;
        waitForTestIdSelectorEnabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorEnabled;
        waitForTestIdSelectorDisabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorDisabled;
        waitForTestIdSelectorClickable: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorClickable;
        waitForTestIdSelectorNotClickable: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorNotClickable;
        waitForTestIdSelectorAriaDisabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorAriaDisabled;
        waitForTestIdSelectorAriaEnabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorAriaEnabled;
        waitForTestIdSelectorAriaChecked: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorAriaChecked;
        waitForTestIdSelectorAriaNotChecked: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorAriaNotChecked;
        waitForTestIdSelectorReadyToPlayVideo: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorReadyToPlayVideo;
        uploadFileInto: import('./config/commands/upload-file-into').UploadFileInto;
        clickInto: import('./config/commands/click-into').ClickInto;
        processTaskQueue: import('./config/commands/process-task-queue').ProcessTaskQueue;
        typeInto: import('./config/commands/type-into').TypeInto;
        assertImage: import('./config/commands/assert-image').AssertImage;
        openPage: import('./config/commands/open-page').OpenPage;
        addUserRole: import('./config/commands/add-user-role').AddUserRole;
        getPath: import('./config/commands/get-path').GetPath;
        getDownloadedFile: import('./config/commands/browser-file-action').GetDownloadedFile;
        deleteDownloadedFile: import('./config/commands/browser-file-action').DeleteDownloadedFile;
        dragAndDrop: import('./config/commands/drag-and-drop').DragAndDrop;
        performScroll: import('./config/commands/perform-scroll').PerformScroll;
        executeSql: import('./config/commands/execute-sql').ExecuteSql;
        clipboardReadText: import('./config/commands/clipboard-read-text').ClipboardReadText;
        executionContext: Hermione.Test;
    }

    /* eslint-enable max-len */
}

declare namespace Hermione {
    type Void = void | Promise<void>;
    type Selector = string | string[];
    type TestContext = Context & {browser: WebdriverIO.Browser};
    type TestDefinitionCallback = (this: TestContext, done: TestDone) => unknown;

    type AssertViewError = Error & {
        stateName: string;
    };
    interface Test {
        id: () => string;
        uuid: string;
        port: number;
        fullTitle(): string;
        file: string;
        hermioneCtx: {assertViewResults?: {_results: Array<AssertViewResultsSuccess | AssertViewError>}};
    }

    interface Config {
        sets?: Record<string, SetsConfig>;
        headless?: boolean;
        strictSSL?: boolean;
    }

    interface RootSuite {
        beforeEach: (callback: (this: Context) => Void) => Void;
        afterEach: (callback: (this: Context) => Void) => Void;
    }
}

declare namespace Chai {
    interface Assertion {
        matchSnapshot: (ctx: Hermione.Context) => void;
    }
}

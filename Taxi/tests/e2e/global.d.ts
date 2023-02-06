declare namespace WebdriverIO {
    import 'hermione/typings/webdriverio';

    /* eslint-disable max-len */

    interface Browser {
        assertBySelector: import('./config/commands/assert-by-selector').AssertBySelector;
        waitUntilRendered: import('./config/commands/wait-until-rendered').WaitUntilRendered;
        waitForTestIdSelectorInDom: import('./config/commands/wait-for-test-id-selector-presence').WaitForTestIdSelectorInDom;
        waitForTestIdSelectorNotInDom: import('./config/commands/wait-for-test-id-selector-presence').WaitForTestIdSelectorNotInDom;
        waitForTestIdSelectorEnabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorEnabled;
        waitForTestIdSelectorDisabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorDisabled;
        waitForTestIdSelectorClickable: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorClickable;
        waitForTestIdSelectorNotClickable: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorNotClickable;
        waitForTestIdSelectorAriaDisabled: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorAriaDisabled;
        waitForTestIdSelectorAriaChecked: import('./config/commands/wait-for-test-id-selector-status').WaitForTestIdSelectorAriaChecked;
        uploadFileInto: import('./config/commands/upload-file-into').UploadFileInto;
        clickInto: import('./config/commands/click-into').ClickInto;
        clickIntoEnsured: import('./config/commands/click-into').ClickIntoEnsured;
        processTaskQueue: import('./config/commands/process-task-queue').ProcessTaskQueue;
        typeInto: import('./config/commands/type-into').TypeInto;
        assertImage: import('./config/commands/assert-image').AssertImage;
        openPage: import('./config/commands/open-page').OpenPage;
        getPath: import('./config/commands/get-path').GetPath;
        getDownloadedFile: import('./config/commands/browser-file-action').GetDownloadedFile;
        deleteDownloadedFile: import('./config/commands/browser-file-action').DeleteDownloadedFile;
        dragAndDrop: import('./config/commands/drag-and-drop').DragAndDrop;
        performScroll: import('./config/commands/perform-scroll').PerformScroll;
        executeSql: import('./config/commands/execute-sql').ExecuteSql;
        removeByTestId: import('./config/commands/remove-by-test-id').RemoveByTestId;
        moveMouseTo: import('./config/commands/move-mouse-to').MoveMouseTo;
        showBySelector: import('./config/commands/show-by-selector').ShowBySelector;
        hideBySelector: import('./config/commands/hide-by-selector').HideBySelector;
        waitForTestIdSelectorDisplayed: import('./config/commands/wait-for-test-id-selector-displayed').WaitForTestIdSelectorDisplayed;
        checkForExistenceByTestId: import('./config/commands/check-for-existence-by-test-id').CheckForExistenceByTestId;
        executionContext: Hermione.Test;
    }

    /* eslint-enable max-len */
}

declare namespace Hermione {
    type Void = void | Promise<void>;

    type Selector = string | string[];

    type TestId = string;
    type GenericSelectorSingle = TestId | {testId: TestId; modifier?: '*' | '^' | '|'} | {selector: string};
    type GenericSelector = GenericSelectorSingle | GenericSelectorSingle[];

    type TestContext = Context & {browser: WebdriverIO.Browser};
    type TestDefinitionCallback = (this: TestContext, done: TestDone) => unknown;

    type IContextDefinition = Mocha.IContextDefinition;

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
        beforeEach: (callback: (this: Mocha.IBeforeAndAfterContext) => Void) => Void;
        afterEach: (callback: (this: Mocha.IBeforeAndAfterContext) => Void) => Void;
    }
}

declare namespace Mocha {
    interface ITest {
        id: () => string;
        uuid: string;
    }

    interface IHookCallbackContext {
        skip(): this;
        timeout(ms: number): this;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        [index: string]: any;
    }

    interface IBeforeAndAfterContext extends IHookCallbackContext {
        currentTest: ITest;
    }
}

declare namespace Chai {
    interface Assertion {
        matchSnapshot: (ctx: Hermione.Context) => void;
    }
}

package ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc;

import ru.yandex.autotests.metrika.appmetrica.data.Application;

public class MtmoblogLayer {

    private Application defaultApplication;
    private Application openEventsApp;
    private Application crashEventsApp;
    private Application errorEventsApp;

    public MtmoblogLayer(Application defaultApplication) {
        this.defaultApplication = defaultApplication;
        this.openEventsApp = defaultApplication;
        this.crashEventsApp = defaultApplication;
        this.errorEventsApp = defaultApplication;
    }

    public Application getDefaultApplication() {
        return defaultApplication;
    }

    public MtmoblogLayer withDefaultApplication(Application defaultApplication) {
        this.defaultApplication = defaultApplication;
        return this;
    }

    public Application getOpenEventsApp() {
        return openEventsApp;
    }

    public MtmoblogLayer withOpenEventsApp(Application openEventsApp) {
        this.openEventsApp = openEventsApp;
        return this;
    }

    public Application getCrashEventsApp() {
        return crashEventsApp;
    }

    public MtmoblogLayer withCrashEventsApp(Application crashEventsApp) {
        this.crashEventsApp = crashEventsApp;
        return this;
    }

    public Application getErrorEventsApp() {
        return errorEventsApp;
    }

    public MtmoblogLayer withErrorEventsApp(Application errorEventsApp) {
        this.errorEventsApp = errorEventsApp;
        return this;
    }
}

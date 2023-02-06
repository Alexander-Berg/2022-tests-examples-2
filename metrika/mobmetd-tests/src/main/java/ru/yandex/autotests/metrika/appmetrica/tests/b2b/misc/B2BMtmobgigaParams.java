package ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc;

public class B2BMtmobgigaParams {

    private B2BAppParams defaultApplication;
    private B2BAppParams openEventsApp;
    private B2BAppParams crashEventsApp;
    private B2BAppParams errorEventsApp;
    private B2BAppParams anrEventsApp;
    private B2BAppParams pushCampaignEventsApp;
    private B2BAppParams clickEventsApp;
    private B2BAppParams installationsApp;
    private B2BAppParams mobmetCampaignsApp;
    private B2BAppParams reengagementEventsApp;
    private B2BAppParams revenueApp;
    private B2BAppParams ecomApp;
    private B2BAppParams skadApp;

    public B2BMtmobgigaParams(B2BAppParams defaultApplication) {
        this.defaultApplication = defaultApplication;
        this.openEventsApp = defaultApplication;
        this.crashEventsApp = defaultApplication;
        this.errorEventsApp = defaultApplication;
        this.anrEventsApp = defaultApplication;
        this.pushCampaignEventsApp = defaultApplication;
        this.clickEventsApp = defaultApplication;
        this.installationsApp = defaultApplication;
        this.mobmetCampaignsApp = defaultApplication;
        this.reengagementEventsApp = defaultApplication;
        this.revenueApp = defaultApplication;
        this.ecomApp = defaultApplication;
        this.skadApp = defaultApplication;
    }

    public B2BAppParams getDefaultApplication() {
        return defaultApplication;
    }

    public B2BMtmobgigaParams withDefaultApplication(B2BAppParams defaultApplication) {
        this.defaultApplication = defaultApplication;
        return this;
    }

    public B2BAppParams getOpenEventsApp() {
        return openEventsApp;
    }

    public B2BMtmobgigaParams withOpenEventsApp(B2BAppParams openEventsApp) {
        this.openEventsApp = openEventsApp;
        return this;
    }

    public B2BAppParams getCrashEventsApp() {
        return crashEventsApp;
    }

    public B2BMtmobgigaParams withCrashEventsApp(B2BAppParams crashEventsApp) {
        this.crashEventsApp = crashEventsApp;
        return this;
    }

    public B2BAppParams getErrorEventsApp() {
        return errorEventsApp;
    }

    public B2BMtmobgigaParams withErrorEventsApp(B2BAppParams errorEventsApp) {
        this.errorEventsApp = errorEventsApp;
        return this;
    }

    public B2BAppParams getAnrEventsApp() {
        return anrEventsApp;
    }

    public B2BMtmobgigaParams withAnrEventsApp(B2BAppParams anrEventsApp) {
        this.anrEventsApp = anrEventsApp;
        return this;
    }

    public B2BAppParams getPushCampaignEventsApp() {
        return pushCampaignEventsApp;
    }

    public B2BMtmobgigaParams withPushCampaignEventsApp(B2BAppParams pushCampaignEventsApp) {
        this.pushCampaignEventsApp = pushCampaignEventsApp;
        return this;
    }

    public B2BAppParams getClickEventsApp() {
        return clickEventsApp;
    }

    public B2BMtmobgigaParams withClickEventsApp(B2BAppParams clickEventsApp) {
        this.clickEventsApp = clickEventsApp;
        return this;
    }

    public B2BAppParams getInstallationsApp() {
        return installationsApp;
    }

    public B2BMtmobgigaParams withInstallationsApp(B2BAppParams installationsApp) {
        this.installationsApp = installationsApp;
        return this;
    }

    public B2BAppParams getMobmetCampaignsApp() {
        return mobmetCampaignsApp;
    }

    public B2BMtmobgigaParams withMobmetCampaignsApp(B2BAppParams mobmetCampaignsApp) {
        this.mobmetCampaignsApp = mobmetCampaignsApp;
        return this;
    }

    public B2BAppParams getReengagementEventsApp() {
        return reengagementEventsApp;
    }

    public B2BMtmobgigaParams withReengagementEventsApp(B2BAppParams reengagementEventsApp) {
        this.reengagementEventsApp = reengagementEventsApp;
        return this;
    }

    public B2BAppParams getRevenueApp() {
        return revenueApp;
    }

    public B2BMtmobgigaParams withRevenueApp(B2BAppParams revenueApp) {
        this.revenueApp = revenueApp;
        return this;
    }

    public B2BAppParams getEcomApp() {
        return ecomApp;
    }

    public B2BMtmobgigaParams withEcomApp(B2BAppParams ecomApp) {
        this.ecomApp = ecomApp;
        return this;
    }

    public B2BAppParams getSkadApp() {
        return skadApp;
    }

    public B2BMtmobgigaParams withSkadApp(B2BAppParams skadApp) {
        this.skadApp = skadApp;
        return this;
    }
}

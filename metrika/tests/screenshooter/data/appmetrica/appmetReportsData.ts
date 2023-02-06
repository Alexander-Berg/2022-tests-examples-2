import { Report } from "../../lib";
import {
    settingsEventsMock,
    getCloudExportsMock,
    androidCrashGroupsGridMock,
    androidCrashGroupsChartMock,
    iosCrashGroupsGridMock,
    userProfilesCountryReportMock,
} from "./appmetricaMocks";


const DEFAULT_REPORT_SELECTOR = ".page-app-statistic__report-content";
const APP_LIST_SELECTOR = ".page-app-list__statistic";
const CRASH_LOG_SELECTOR = ".eMAGH";
const CAMPAIGN_LIST_SELECTOR = ".page-campaign-list__content";
const PARTNERS_LIST_SELECTOR =".page-partner-list";
const PUSH_CAMPAIGN_LIST_SELECTOR = ".page-push-campaign-list__main";
const APP_SETTINGS_SELECTOR = ".page-app-settings";
const EXPORT_TO_FILE_SELECTOR =".page-app-export-logs";
const EXPORT_TO_CLOUD_SELECTOR =".page-app-cloud-edit";
const DEFAULT_LOADER_SELECTOR = ".spin2";
const CRASH_LOG_LOADER_SELECTOR = ".iPvcNo";


export const appmetReports: Report[] = [
    //UA
    {
        url: "/statistic?from=2021-01-01&to=2021-01-31&appId=3679333&report=campaigns2&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"deeplinks\"],[\"conversion\"]]" +
            "&sampling=1" +
            "&chartType=pie" +
            "&sort=-[\"installs\"]" +
            "&chartColumn=installs" +
            "&dimensions=[[\"publisher\"],[\"tracker\"]]" +
            "&selected=[\"[[\"0\"]]\",\"[[\"43\"]]\",\"[[\"69378\"]]\"]",
        name: '"UA - piechart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2021-01-01&to=2021-01-31&appId=3679333&report=campaigns2&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"deeplinks\"],[\"conversion\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"clicks\"]" +
            "&tableView=drilldown" +
            "&chartColumn=installs"+
            "&dimensions=[[\"publisher\"]%2C[\"tracker\"]]" +
            "&selected=[\"[[\"0\"]]\",\"[[\"43\"]]\",\"[[\"69378\"]]\"]",
        name: '"UA - multiline chart and drilldown"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2021-01-25&to=2021-01-26&appId=28554&report=campaigns2&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"deeplinks\"],[\"conversion\"],[\"purchases\"],[\"revenue\"]," +
                "[\"retention\",{\"type\":\"day\",\"count\":1}],[\"eventsPerUser\"," +
                "[\"App2app.+Разрешил+доступ+к+микрофону\"]]]" +
            "&sampling=1&tablePath=[[\"254\"]]" +
            "&chartType=multiline" +
            "&sort=-[\"clicks\"]" +
            "&tableView=multilevel" +
            "&chartColumn=[\"chartInstalls\",\"uaChartClicks\",\"uaChartDeeplinks\"]" +
            "&dimensions=[[\"publisher\"],[\"tracker\"]]" +
            "&selected=[\"[[\"254\"],[\"312998480626872000\",\"254\"]]\",\"[[\"254\"]," +
                "[\"889477937512852395\",\"254\"]]\"," +
                "\"[[\"254\"],[\"1105623043193003414\",\"254\"]]\",\"[[\"254\"]," +
                "[\"24759133597095813\",\"254\"]]\",\"[[\"254\"],[\"98634495518919537\",\"254\"]]\"]",
        name: '"UA - multiple metrics in chart, deeplinks in metrics"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-01-15&to=2020-01-31&appId=28554&report=campaigns2&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"purchases\"],[\"revenue\"],[\"loyalUsers\",3]]" +
            "&sampling=1&" +
            "chartType=multiline" +
            "&sort=-[\"clicks\"]" +
            "&tableView=multilevel" +
            "&chartColumn=[\"chartInstalls\"]" +
            "&dimensions=[[\"operatingSystemInfo\"],[\"gender\"],[\"ageInterval\"]]" +
            "&selected=[\"[[\"android\"]]\",\"[[\"iOS\"]]\",\"[[null]]\"]",
        name: '"UA - group by OS, gender, age"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-01-15&to=2020-01-31&appId=28554&report=campaigns2&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"purchases\"],[\"revenue\"],[\"loyalUsers\",3]]" +
            "&sampling=1&" +
            "&chartType=multicolumn" +
            "&sort=-[\"clicks\"]" +
            "&tableView=multilevel" +
            "&chartColumn=[\"chartInstalls\"]" +
            "&currency=RUB" +
            "&dimensions=[[\"operatingSystemInfo\"],[\"gender\"],[\"ageInterval\"]]" +
            "&selected=[\"[[\"android\"],[\"male\"],[null]]\",\"[[\"android\"],[\"male\"],[\"17\"]]\"," +
                "\"[[\"android\"],[\"male\"],[\"18\"]]\"]",
                name: '"UA - group by OS, gender, age multilevel chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },

    {
        url: "/statistic?from=2020-01-25&to=2020-01-31&appId=28554&report=campaigns2&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"revenue\"],[\"eventUsers\",\"" +
                "[\"eventsCount\",[\"\\\"О+модели\\\".+Действия\",\"\\\"О + модели\\\".+Загрузки+экранов\"]]," +
                "[\"loyalUsers\",3]]" +
            "&sampling=1" +
            "&chartType=multicolumn" +
            "&sort=-[\"clicks\"]" +
            "&tableView=multilevel" +
            "&chartColumn=[\"chartInstalls\"]" +
            "&currency=EUR" +
            "&dimensions=[[\"publisher\"],[\"tracker\"],[\"urlParam\",\"utm_source\"]," +
                "[\"operatingSystemInfo\"],[\"operatingSystemVersionInfo\"],[\"gender\"]]" +
            "&selected=[\"[[\"254\"]]\",\"[[\"68193\"]]\",\"[[\"44\"]]\"]",
        name: '"UA - group by a huge amount of dimensions, metric by event name"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Remarketing
    {
        url: "/statistic?from=2020-03-01&to=2020-03-31&appId=130830&report=remarketing&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"reengagement\"],[\"deeplinks\"],[\"conversion\"]," +
                "[\"eventConversion\",[\"AddFunds\"]],[\"retention\",{\"type\":\"week\",\"count\":1}]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"reengagement\"]" +
            "&chartColumn=[\"chartReengagement\"]" +
            "&dimensions=[[\"publisher\"],[\"tracker\"]]" +
            "&selected=[\"[[\"89095\"]]\"," +
                "\"[[\"30101\"]]\",\"[[\"47150\"]]\"]",
        name: '"Remarketing multiline chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-03-01&to=2020-03-31&appId=130830&report=remarketing&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"reengagement\"],[\"conversion\"],[\"eventsCount\",[\"ActivationPinScreen\"," +
                "\"ActivationCardSuccess\",\"AccountManager\"]],[\"purchases\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"reengagement\"]" +
            "&tableView=drilldown" +
            "&chartColumn=[\"chartReengagement\"]" +
            "&dimensions=[[\"publisher\"],[\"tracker\"],[\"operatingSystemVersionInfo\"],[\"gender\"]]" +
            "&selected=[\"[[\"89095\"]]\",\"[[\"30101\"]]\",\"[[\"47150\"]]\"]",
        name: '"Remarketing multiline chart drilldown"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-03-01&to=2020-03-31&appId=130830&report=remarketing&filters={\"values\":[]}" +
            "&metrics=[[\"clicks\"],[\"reengagement\"],[\"conversion\"]," +
                "[\"eventsCount\",[\"ActivationPinScreen\",\"ActivationCardSuccess\",\"AccountManager\"]]," +
                "[\"purchases\"]]" +
            "&sampling=1" +
            "&tablePath=[[\"89095\"],[\"674973330914181456\",\"89095\"],[\"10\",\"android\"]]" +
            "&chartType=pie" +
            "&sort=-[\"reengagement\"]" +
            "&tableView=multilevel" +
            "&chartColumn=[\"chartReengagement\"]" +
            "&dimensions=[[\"publisher\"],[\"tracker\"],[\"operatingSystemVersionInfo\"],[\"gender\"]]" +
            "&selected=[\"[[\"89095\"],[\"674973330914181456\",\"89095\"],[\"10\",\"android\"]," +
                "[\"male\"]]\",\"[[\"89095\"],[\"674973330914181456\",\"89095\"]," +
                "[\"10\",\"android\"],[\"female\"]]\",\"[[\"89095\"],[\"674973330914181456\"," +
                "\"89095\"],[\"10\",\"android\"],[null]]\"]",
        name: '"Remarketing pie chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Retention analyzsis

    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=retention&filters={\"values\":[]}" +
            "&metrics=ym_i_users" +
            "&sampling=1" +
            "&cohortType=installation_date" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&retention=dynamics" +
            "&splitBy=day",
        name: '"Retention dynamics by install date"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2021-06-01&to=2021-06-07&appId=28554&report=retention" +
            "&metrics=ym_ge_users" +
            "&sampling=1" +
            "&segmentId=0" +
            "&cohortType=partner" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&retention=rolling" +
            "&splitBy=week",
        name: '"Rolling retention by partners"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=retention" +
            "&metrics=ym_ge_users" +
            "&sampling=1" +
            "&segmentId=0" +
            "&cohortType=tracker" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&retention=classic",
        name: '"Retention by tracker"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=retention" +
            "&metrics=ym_ge_users" +
            "&sampling=1" +
            "&segmentId=0" +
            "&cohortType=tracker_param" +
            "&trackerParamKey=utm_source" +
            "&minCohortSize=1" +
            "&retention=classic",
        name: '"Retention by tracker param"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Cohort analysis
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=cohort" +
            "&metrics=ym_ge_users" +
            "&sampling=1" +
            "&segmentId=0" +
            "&cohortType=installation_date" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&conversionEventName=defaultConversionEventName" +
            "&retention=classic",
        name: '"Cohort by install date and default event"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2021-06-01&to=2021-06-07&appId=28554&report=cohort" +
            "&metrics=ym_ge_users" +
            "&sampling=1" +
            "&segmentId=0" +
            "&cohortType=partner" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&conversionEventName=CH_OFFER_SHOW" +
            "&retention=classic",
        name: '"Cohort by partner, count sessions by custom event"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=cohort&" +
            "&metrics=ym_ge_users" +
            "&sampling=0.1" +
            "&segmentId=0" +
            "&cohortType=region_city" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&conversionEventName=Просмотр+объявления" +
            "&cohortSettingsMetric=devices" +
            "&retention=classic" +
            "&splitBy=day",
        name: '"Cohort by city, count users by custom event"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Revenue
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=revenue" +
            "&requested_uid=178121744&metrics=[[\"payingUsersWithNorm\"],[\"purchasesWithNorm\"]," +
                "[\"purchasesPerUser\"],[\"revenueWithNorm\"],[\"arpu\"],[\"arppu\"],[\"payingUsersPercentage\"]]" +
            "&sampling=1" +
            "&tableRoot=date" +
            "&chartType=multiline" +
            "&sort=-[\"datePeriodday\"]" +
            "&chartColumn=[\"revenue\"]" +
            "&dimensions=[[\"datePeriodday\"]]" +
            "&selected=[\"__all__\"]",
        name: '"Revenue group by day"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=revenue" +
            "&metrics=[[\"payingUsersWithNorm\"],[\"purchasesWithNorm\"],[\"purchasesPerUser\"]," +
            "[\"revenueWithNorm\"],[\"arpu\"],[\"arppu\"],[\"payingUsersPercentage\"],[\"verifiedRevenue\"]," +
            "[\"averageOrderValue\"]]" +
            "&sampling=1" +
            "&tableRoot=currency" +
            "&chartType=multiline" +
            "&sort=-[\"payingUsersWithNorm\"]" +
            "&chartColumn=[\"revenue\"]" +
            "&dimensions=[[\"revenueProductId\"],[\"revenueOrderId\"]]" +
            "&selected=[\"[[\"ru.yandex.mobile.music.1month.autorenewable.1month.trial.plus.169.as\"]]\"," +
                "\"[[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.plus.169\"]]\"," +
                "\"[[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.169\"]]\"]",
        name: '"Revenue group by products"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url:"/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=revenue" +
            "&metrics=[[\"payingUsersWithNorm\"],[\"purchasesWithNorm\"],[\"purchasesPerUser\"]," +
                "[\"revenueWithNorm\"],[\"arpu\"],[\"arppu\"],[\"payingUsersPercentage\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"payingUsersWithNorm\"]" +
            "&tableView=drilldown" +
            "&chartColumn=[\"revenue\"]" +
            "&currency=USD" +
            "&dimensions=[[\"ageInterval\"],[\"gender\"],[\"appVersionDetails\"],[\"revenueProductId\"]]" +
            "&selected=[\"[[\"25\"],[\"female\"],[\"454+(iOS)\"]," +
                "[\"ru.yandex.mobile.music.1month.autorenewable.1month.trial.plus.169.as\"]]\"," +
                "\"[[\"25\"],[\"female\"],[\"454+(iOS)\"]," +
                "[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.plus.169\"]]\"," +
                "\"[[\"25\"],[\"female\"],[\"454+(iOS)\"]," +
                "[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.169\"]]\"]",
        name: '"Revenue drilldown multiline chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=revenue" +
            "&metrics=[[\"payingUsersWithNorm\"],[\"purchasesWithNorm\"],[\"purchasesPerUser\"]," +
            "[\"revenueWithNorm\"],[\"arpu\"],[\"arppu\"],[\"payingUsersPercentage\"],[\"verifiedRevenue\"]," +
            "[\"averageOrderValue\"]]" +
            "&sampling=1" +
            "&tableRoot=currency" +
            "&chartType=multicolumn" +
            "&sort=-[\"payingUsersWithNorm\"]" +
            "&chartColumn=[\"arppu\",\"revenue\"]" +
            "&dimensions=[[\"revenueProductId\"],[\"revenueOrderId\"]]" +
            "&selected=[\"[[\"ru.yandex.mobile.music.1month.autorenewable.1month.trial.plus.169.as\"]]\"," +
            "\"[[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.plus.169\"]]\"," +
            "\"[[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.169\"]]\"]",
        name: '"Revenue multicolumn chart with 2 metrics"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=revenue" +
            "&metrics=[[\"payingUsersWithNorm\"],[\"purchasesWithNorm\"],[\"purchasesPerUser\"]," +
            "[\"revenueWithNorm\"],[\"arpu\"],[\"arppu\"],[\"payingUsersPercentage\"],[\"verifiedRevenue\"]," +
            "[\"averageOrderValue\"]]" +
            "&sampling=1" +
            "&tableRoot=currency" +
            "&chartType=pie" +
            "&sort=-[\"payingUsersWithNorm\"]" +
            "&chartColumn=[\"purchases\"]" +
            "&dimensions=[[\"revenueProductId\"],[\"revenueOrderId\"]]" +
            "&selected=[\"[[\"ru.yandex.mobile.music.1month.autorenewable.1month.trial.plus.169.as\"]]\"," +
            "\"[[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.plus.169\"]]\"," +
            "\"[[\"ru.yandex.mobile.music.1month.autorenewable.3month.trial.169\"]]\"]",
        name: '"Revenue pie chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Audience
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=audience" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&segmentId=0" +
            "&retention=classic" +
            "&tableRoot=date" +
            "&chartType=line" +
            "&sort=-ym:u:date",
        name: '"Audience by Date line chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=audience" +
            "&dimensionValues=%5B%22225%22%5D;%5B%22187%22%5D;%5B%22159%22%5D" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&segmentId=0" +
            "&retention=classic" +
            "&tableRoot=country" +
            "&chartType=stacked-area" +
            "&sort=-ym:u:activeUsers",
        name: '"Audience by Country stacked chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=audience" +
            "&dimensionValues=%5B%22225%22%2C%221%22%5D;%5B%22225%22%2Cnull%5D;%5B%22225%22%2C%2210174%22%5D" +
            "&requested_uid=178121744" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&segmentId=0" +
            "&retention=classic" +
            "&tableRoot=region" +
            "&chartType=multicolumn" +
            "&sort=-ym:u:activeUser",
        name: '"Audience by Region multicolumn chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=audience" +
            "&dimensionValues=[\"225\",\"1\",\"213\"];[\"225\",null,null];[\"225\",\"10174\",\"2\"]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&segmentId=0" +
            "&retention=classic" +
            "&tableRoot=city" +
            "&chartType=stacked-column" +
            "&sort=-ym:u:activeUsers",
        name: '"Audience by City stacked-column chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=audience" +
            "&dimensionValues=[\"male\"];[null];[\"female\"]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&segmentId=0" +
            "&retention=classic" +
            "&tableRoot=gender" +
            "&chartType=pie" +
            "&sort=-ym:u:activeUsers",
        name: '"Audience by Gender pie chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=audience" +
            "&dimensionValues=[\"25\"];[\"35\"];[null]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&segmentId=0" +
            "&retention=classic" +
            "&tableRoot=age" +
            "&chartType=multiline" +
            "&sort=-ym:u:activeUsers",
        name: '"Audience by Age multiline chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
        // User Profiles
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=users-profiles" +
            "&dimensionValues=[\"225\"];[\"159\"];[\"149\"];[\"171\"];[\"187\"]" +
            "&metrics=ym_p_users" +
            "&sampling=1" +
            "&tableRoot=ym:p:regionCountry",
        name: '"User profiles by Country pie chart"',
        mocks:[userProfilesCountryReportMock],
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=25378&report=users-profiles" +
            "&dimensionValues=[\"YANDEX\"];[\"yandex\"];[\"PDD\"];[\"social:vk\"];[\"GOOGLE_PLUS\"]" +
            "&metrics=ym_p_users" +
            "&sampling=0.1" +
            "&tableRoot=ym:p:customStringAttribute2962" +
            "&chartType=multicolumn",
        name: '"User profiles by custom attribute multicolumn chart"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Events
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=events" +
            "&dimensionValues=[\"Выдача. Просмотр сниппета\"];[\"Показ сниппета\"];[\"ad_requested\"]" +
            "&metrics=ym_ce2_usersWithEvent" +
            "&sampling=1" +
            "&tableRoot=eventLevel0" +
            "&chartType=multiline" +
            "&sort=-ym:ce2:usersWithEvent" +
            "&tableOption=eventsUsers",
        name: '"Events group by users"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=events" +
            "&dimensionValues=[\"Выдача. Просмотр сниппета\"];[\"Показ сниппета\"];[\"ad_requested\"]" +
            "&metrics=ym_ce2_usersWithEvent" +
            "&sampling=1" +
            "&tableRoot=eventLevel0" +
            "&chartType=multicolumn" +
            "&sort=-allEvents" +
            "&tableOption=devices" +
            "&chartColumn=devices",
        name: '"Events group by devices"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=events" +
            "&dimensionValues=[\"Выдача. Просмотр сниппета\"];[\"Показ сниппета\"];[\"ad_requested\"];" +
            "[\"Выдача. Просмотр сниппета\",\"Тип\"];[\"Выдача. Просмотр сниппета\",\"Тип\",\"обычный\"]" +
            "&metrics=ym_ce2_usersWithEvent" +
            "&sampling=1" +
            "&tableRoot=eventLevel0" +
            "&chartType=stacked-area" +
            "&sort=-allEvents" +
            "&tableOption=device" +
            "s&tableView=drilldown" +
            "&chartColumn=devices",
        name: '"Events group by devices drilldown"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=events" +
            "&dimensionValues=[\"Показ сниппета\",\"Индекс\",\"0\"];[\"Показ сниппета\",\"Индекс\",\"1\"];" +
            "[\"Показ сниппета\",\"Индекс\",\"2\"]" +
            "&metrics=ym_ce2_usersWithEvent" +
            "&sampling=1" +
            "&tableRoot=eventLevel0" +
            "&chartType=multiline" +
            "&sort=-fgEvents" +
            "&tableOption=users" +
            "&tableView=multilevel" +
            "&tableLevels=[\"Показ+сниппета\",\"Индекс\"]" +
            "&chartColumn=usersPercentage",
        name: '"Events group by users multilevel table view"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Android Crashes
    {
        url: "/statistic?from=2019-09-01&to=2019-09-30&group=day" +
            "&sampling=1&appId=25378&report=crash-logs-android&tableRoot=crashGroup",
        name: '"Android Crashes group by crash groups"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
        ignoreElements: [".sc-bMVAic.bTsVKB .sc-hORach:first-child"],
        mocks: [androidCrashGroupsGridMock, androidCrashGroupsChartMock]
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-android&tableRoot=appVersionName",
        name: '"Android Crashes group by app version name"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-android&tableRoot=operatingSystemVersion",
        name: '"Android Crashes group by operating system version"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-android&tableRoot=mobileDeviceBranding",
        name: '"Android Crashes group by manufacturer"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-android&tableRoot=mobileDeviceModel",
        name: '"Android Crashes group by device model"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-09-01&to=2019-09-30&group=day&appId=25378" +
            "&report=crash-logs-android&sampling=1&crashGroupId=12454995534919700191",
        name: '"Android Crash group detailed"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-09-01&to=2019-09-30&group=day&sampling=1&appId=25378" +
            "&report=crash-logs-android&crashGroupId=12454995534919700191&selectedCrashId=696519162778090898",
        name: '"Android Crash log"',
        selector: CRASH_LOG_SELECTOR,
        loaderSelector: CRASH_LOG_LOADER_SELECTOR,
    },
    // iOS Crashes
    {
        url: "/statistic?from=2019-09-01&to=2019-09-30&group=day" +
            "&sampling=1&appId=25378&report=crash-logs-ios&tableRoot=crashGroup",
        name: '"iOS Crashes group by crash groups"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
        mocks: [iosCrashGroupsGridMock]
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-ios&tableRoot=appVersionName",
        name: '"iOS Crashes group by app version name"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-ios&tableRoot=operatingSystemVersion",
        name: '"iOS Crashes group by operating system version"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?group=day&to=2019-09-30&from=2019-09-01" +
            "&sampling=1&appId=25378&report=crash-logs-ios&tableRoot=mobileDeviceModel",
        name: '"iOS Crashes group by device model"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-09-01&to=2019-09-30&group=day&appId=25378" +
            "&report=crash-logs-ios&sampling=1&crashGroupId=570462385381130762",
        name: '"iOS Crash group detailed"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-09-01&to=2019-09-30&group=day&appId=25378&report=crash-logs-ios" +
            "&sampling=1&crashGroupId=570462385381130762&selectedCrashId=12181243125047984634",
        name: '"iOS Crash log"',
        selector: CRASH_LOG_SELECTOR,
        loaderSelector: CRASH_LOG_LOADER_SELECTOR,
    },
    //Engagement
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=engagement" +
            "&metrics=[[\"totalSessionDurationPerUser\"],[\"sessionsCount\"],[\"sessionsPerUser\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"totalSessionDurationPerUser\"]&chartColumn=[\"totalSessionDurationPerUser\"]" +
            "&dimensions=[[\"datePeriodday\"]]" +
            "&selected=[\"__all__\"]",
        name: '"Engagement group by day"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=engagement" +
            "&metrics=[[\"totalSessionDurationPerUser\"],[\"sessionsCount\"],[\"sessionsPerUser\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"totalSessionDurationPerUser\"]" +
            "&chartColumn=[\"totalSessionDurationPerUser\"]" +
            "&dimensions=[[\"sessionTimeInterval\"]]" +
            "&selected=[\"[[\"36000\"]]\",\"[[\"18000\"]]\",\"[[\"7200\"]]\"]",
        name: '"Engagement group by session duration"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // other reports
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=push-campaigns" +
            "&metrics=[[\"sentDevices\"],[\"receivedDevices\"],[\"openedDevices\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"sentDevices\"]" +
            "&chartColumn=[\"sentDevices\",\"receivedDevices\",\"openedDevices\"]" +
            "&dimensions=[[\"campaignInfo\"],[\"hypothesisOrTag\"],[\"operatingSystemInfo\"],[\"messageLang\"]]" +
            "&selected=[\"[[\"campaign.104998\"]]\",\"[[\"campaign.110694\"]]\",\"[[\"campaign.104281\"]]\"]",
        name: '"Push campaigns report"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=app-version&sampling=1",
        name: '"App version"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=operating-system-version&sampling=1",
        name: '"Operating system version"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=mobile-branding&sampling=1",
        name: '"Manufacturers"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=mobile-model&sampling=1",
        name: '"Device model"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=device-type&sampling=1",
        name: '"Device type"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=locale&sampling=1",
        name: '"Locale"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=resolutions&sampling=1",
        name: '"Screen resolutions"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=root-status&sampling=1",
        name: '"Root-status"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=sdk-version&sampling=1",
        name: '"SDK version"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=operator&sampling=1",
        name: '"Carriers"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-06-01&to=2019-07-15&appId=28554&report=network-type&sampling=1",
        name: '"Connection type"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // SKAD network
    {
        url: "/statistic?from=2021-09-01&to=2021-09-30&appId=28620&report=skadnetwork" +
            "&metrics=[[\"installationsAll\"],[\"installationsNew\"],[\"reinstallations\"]," +
            "[\"targetActions\"],[\"engagementEventsCount\"],[\"revenueTotalRevenue\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"installationsAll\"]" +
            "&chartColumn=installationsAll" +
            "&dimensions=[[\"adNetworkName\"],[\"skadCampaignID\"]]" +
            "&selected=[\"[[\\\"Yandex.Direct\\\"]]\",\"[[\\\"Abc123.skadnetwork\\\"]]\"," +
            "\"[[\\\"Abc123.skadnetwork.model3.revenue\\\"]]\"]",
        name: '"SKAD network"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // App List
    {
        url: "/application/list?from=2021-09-01&to=2021-09-14&groupId=6610&metrics=ym_ge_users&sampling=1",
        name: '"App statistics in app list"',
        selector: APP_LIST_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Trackers
    {
        url: "/campaign/list?appId=7633&showArchived=true&sampling=1",
        name: '"Trackers"',
        selector: CAMPAIGN_LIST_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Media Sources
    {
        url: "/partner/list?&showArchived=true&sampling=1",
        name: '"Media Sources"',
        selector: PARTNERS_LIST_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Push campaigns
    {
        url: "/push-campaign/list?appId=284530&requested_uid=178121744&pageNum=1&pageSize=25",
        name: '"Push Campaigns list"',
        selector: PUSH_CAMPAIGN_LIST_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // App settings
    {
        url: "/application/edit?appId=1&sampling=1",
        name: '"App settings - General"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=grants&sampling=1",
        name: '"App settings - Manage Access"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=revenue&sampling=1",
        name: '"App settings - Revenue"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=push-notification-settings&sampling=1",
        name: '"App settings - Push notifications"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=targeturls&sampling=1",
        name: '"App settings - Destination URLs"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=deeplinks&sampling=1",
        name: '"App settings - Deeplinks"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=test-devices&sampling=1",
        name: '"App settings - Test devices"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=profiles&sampling=1",
        name: '"App settings - Profile attributes"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=1&type=events&sampling=1",
        name: '"App settings - Events Settings"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
        mocks: [settingsEventsMock]
    },
    {
        url: "/application/edit?appId=1&type=crash-upload&platform=android&crashPage=files&sampling=1",
        name: '"App settings - Crashes, Android, Upload files"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Data export
    {
        url: "/application/export-logs?appId=28554",
            name: '"Data export to file - clicks',
        selector: EXPORT_TO_FILE_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/cloud?appId=185600",
            name: '"Data export to the Cloud"',
        selector: EXPORT_TO_CLOUD_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
        mocks: [getCloudExportsMock]
    },
    // App settings - agent
    {
        url: "/application/edit?appId=2",
        name: '"Agent app settings URLs"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=2&type=deeplinks",
        name: '"Agent app settings deeplinks"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=2&type=test-devices",
        name: '"Agent app settings test devices"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // App settings - guest
    {
        url: "/application/edit?appId=806979",
        name: '"Guest app settings"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=grants",
        name: '"Guest app settings - grants"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=push-notification-settings",
        name: '"Guest app settings - push"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=targeturls",
        name: '"Guest app settings - URLS"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=deeplinks",
        name: '"Guest app settings - deeplinks"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=test-devices",
        name: '"Guest app settings - test devices"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=profiles",
        name: '"Guest app settings - profiles"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/application/edit?appId=806979&type=events",
        name: '"Guest app settings - events"',
        selector: APP_SETTINGS_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
        mocks: [settingsEventsMock]
    },
    // Reports for agent
    {
        url: "/statistic?from=2022-02-01&to=2022-02-15&appId=2&report=campaigns2" +
            "&metrics=[[\"clicks\"],[\"installs\"],[\"deeplinks\"],[\"conversion\"],[\"sessions\"]]" +
            "&sampling=1" +
            "&chartType=multiline" +
            "&sort=-[\"installs\"]" +
            "&chartColumn=[\"chartInstalls\"]" +
            "&dimensions=[[\"publisher\"],[\"tracker\"]]" +
            "&selected=[\"[[\\\"254\\\"]]\"]",
        name: '"UA - agent"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-12-01&to=2020-12-15&group=day&appId=2&report=cohort" +
            "&metrics=ym_i_users" +
            "&sampling=1" +
            "&cohortType=partner" +
            "&trackerParamKey=&" +
            "minCohortSize=1" +
            "&conversionEventName=defaultConversionEventName" +
            "&cohortSettingsMetric=events" +
            "&retention=classic" +
            "&splitBy=day",
        name: '"Cohort analysis - agent"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-12-01&to=2020-12-15&group=day&appId=2&report=cohort" +
            "&metrics=ym_i_users" +
            "&sampling=1" +
            "&cohortType=partner" +
            "&trackerParamKey=&" +
            "minCohortSize=1" +
            "&conversionEventName=defaultConversionEventName" +
            "&cohortSettingsMetric=events" +
            "&retention=classic" +
            "&splitBy=day",
        name: '"Audience - agent"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Segmentation
    {
        url: "/statistic?from=2018-10-01&to=2018-10-31&appId=10267&report=events" +
            "&filters={\"values\":[{\"id\":\"userClientEvents\",\"data\":" +
            "{\"paths\":[{\"path\":[\"A:FilmScreenScroll\"]},{\"path\":[\"A:FilmDetailsView\",\"auth\"]}," +
            "{\"path\":[\"A:MainPageGalleryItemView\",\"auth\",\"yes\"]}]," +
            "\"inverted\":false,\"combinePolicy\":\"or\",\"to\":\"2018-10-31\"," +
            "\"from\":\"2018-10-01\"}},{\"id\":\"userClientEvents\",\"data\":{\"paths\":" +
            "[{\"path\":[\"E:BannerOnPersonLoadError\"]},{\"path\":[\"NE:Connection\"]}]," +
            "\"inverted\":true,\"combinePolicy\":\"and\",\"to\":\"2018-10-31\",\"from\":\"2018-10-01\"}}]}" +
            "&dimensionValues=[\"A:MainPageGalleryItemView\"];[\"A:FilmDetailsView\"];[\"M:FilmDetailView\"]" +
            "&metrics=ym_ce2_usersWithEvent" +
            "&sampling=0.01" +
            "&tableRoot=eventLevel0" +
            "&chartType=multiline" +
            "&sort=-ym:ce2:usersWithEvent" +
            "&tableOption=eventsUsers",
        name: '"Events with filters"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2022-03-30&to=2022-04-05&appId=806976&report=audience" +
            "&filters={\"values\":[{\"id\":\"userGender\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"male\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"userAge\",\"data\":{\"inverted\":false,\"values\":[{\"value\":\"17\",\"operator\":\"==\"}]}}]}" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&tableRoot=date" +
            "&chartType=line" +
            "&sort=-ym:u:date",
        name: '"Audience with demography filters"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2020-01-01&to=2020-01-12&appId=806976&report=audience" +
            "&filters={\"values\":[{\"id\":\"startDates\",\"data\":{\"from\":\"2018-10-01\",\"to\":\"2018-10-31\"}}]}" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&tableRoot=date" +
            "&chartType=line" +
            "&sort=-ym:u:date",
        name: '"Audience with app-start filter"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2018-10-01&to=2018-10-31&appId=806976&report=audience" +
            "&filters={\"values\":[{\"id\":\"installDates\",\"data\":{\"from\":\"2018-10-01\",\"to\":\"2018-10-31\"}}," +
            "{\"id\":\"installPublisher\",\"data\":{\"inverted\":false," +
            "\"values\":[{\"value\":\"0\",\"operator\":\"==\"},{\"value\":\"69147\"," +
            "\"operator\":\"==\"}]}},{\"id\":\"installCampaign\",\"data\":{\"inverted\":false," +
            "\"values\":[{\"value\":\"313515728219183472\",\"operator\":\"==\"},{\"value\":\"889976466748564581\"," +
            "\"operator\":\"==\"}]}},{\"id\":\"installTrackerParams\"," +
            "\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"from\"]}," +
            "{\"path\":[\"referrer\"]}]}},{\"id\":\"installGeo\",\"data\":{\"inverted\":false," +
            "\"paths\":[{\"path\":[\"225\"]}]}},{\"id\":\"installOS\",\"data\":{\"inverted\":false," +
            "\"paths\":[{\"path\":[\"android\"]},{\"path\":[\"iOS\"]}]}},{\"id\":\"installAppVersion\"," +
            "\"data\":{\"inverted\":false,\"values\":[{\"value\":\"1.04+(Android)\",\"operator\":\"==\"}]}}]}" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&tableRoot=date" +
            "&chartType=line" +
            "&sort=-ym:u:date",
        name: '"Audience with installs filter"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2018-10-01&to=2018-11-30&appId=806976&report=audience" +
            "&filters={\"values\":[{\"id\":\"openPublisher\",\"data\":{\"inverted\":false,\"values\":" +
            "[{\"value\":\"0\",\"operator\":\"==\"}]}},{\"id\":\"openDates\",\"data\":{\"from\":\"2018-10-01\"," +
            "\"to\":\"2018-10-31\"}},{\"id\":\"openCampaign\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"0\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"openTrackerParams\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"action\"]}," +
            "{\"path\":[\"client_id\"]}," +
            "{\"path\":[\"code_challenge\"]}]}}]}&dimensionValues=[\"225\",\"1\"];[\"225\",null];[\"225\",\"10174\"]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=1" +
            "&tableRoot=region" +
            "&chartType=stacked-area" +
            "&sort=-ym:u:activeUsers",
        name: '"Audience with deeplinks filter"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2018-10-01&to=2018-10-31&appId=10267&report=push-campaigns" +
            "&filters={\"values\":[{\"id\":\"pushSent\",\"data\":{\"inverted\":false,\"paths\":" +
            "[{\"path\":[\"71663.null\"]},{\"path\":[\"69559.null\"]},{\"path\":[\"70093.null\"]}]}}," +
            "{\"id\":\"pushReceived\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"71663.null\"]}," +
            "{\"path\":[\"69559.null\"]},{\"path\":[\"69013.null\"]}]}},{\"id\":\"pushOpened\",\"data\":" +
            "{\"inverted\":true,\"paths\":[{\"path\":[\"70801.null\"]}]}},{\"id\":\"pushSkipped\",\"data\":" +
            "{\"inverted\":false,\"paths\":[{\"path\":[\"70822.null\"]}]}},{\"id\":\"pushZeroHypo\",\"data\":" +
            "{\"inverted\":false,\"paths\":[{\"path\":[\"70093.null\"]}]}}]}" +
            "&dimensionValues=71663.null;69559.null" +
            "&metrics=ym_pc_sentDevices" +
            "&sampling=0.06507",
        name: '"Audience with push-campaigns filter"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2018-10-01&to=2018-10-31&appId=10267&report=app-version" +
            "&filters={\"values\":[{\"id\":\"daysSinceInstall\",\"data\":{\"value\":\"1\",\"operator\":\">\"}}," +
            "{\"id\":\"daysSinceLastVisit\",\"data\":{\"value\":\"100\",\"operator\":\"<\"}}," +
            "{\"id\":\"sessionsCount\",\"data\":{\"value\":\"99\",\"operator\":\"!=\"}}," +
            "{\"id\":\"crashesCount\",\"data\":{\"operator\":\"<>\",\"value\":[\"1\",\"100\"]}}," +
            "{\"id\":\"pushNotificationOpened\",\"data\":{\"value\":\"1\",\"operator\":\">\"}}]}" +
            "&dimensionValues=4.5.4%20(Android);4.5.2%20(Android);4.3.0%20(Android)" +
            "&metrics=ym_t_devices" +
            "&sampling=0.1",
        name: '"App-version with lifetime filters"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-08-01&to=2019-08-31&appId=10267&report=audience" +
            "&filters={\"values\":[{\"id\":\"userGender\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"male\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"commonOS\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"iOS\"]}]}}," +
            "{\"id\":\"commonGeo\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"149\",\"29630\",\"157\"]}]}}," +
            "{\"id\":\"userDeviceBrand\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"Apple\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"commonBuildNumber\",\"data\":{\"inverted\":false,\"values\":[{\"value\":\"7984+(iOS)\"," +
            "\"operator\":\"==\"}]}}]}" +
            "&dimensionValues=[\"225\",\"1\",\"213\"];[\"225\",null,null];" +
            "[\"225\",\"10174\",\"2\"];[\"149\",\"29630\",\"157\"]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=0.01" +
            "&tableRoot=city" +
            "&chartType=stacked-area" +
            "&sort=-ym:u:activeUsers",
        name: '"Audience with various kind of filters"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2018-10-01&to=2018-10-31&appId=10267&report=audience" +
            "&filters={\"values\":[{\"id\":\"userDeviceID\",\"data\":{\"value\":\"44\"," +
            "\"operator\":\"==\"}},{\"id\":\"userDevice\",\"data\":" +
            "{\"value\":\"24\",\"operator\":\"==\"}},{\"id\":\"userIosIFA\",\"data\":" +
            "{\"value\":\"343\",\"operator\":\"==\"}}]}" +
            "&dimensionValues=[\"225\",\"1\",\"213\"];[\"225\",null,null];[\"225\",\"10174\",\"2\"]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=0.1" +
            "&segmentId=0" +
            "&tableRoot=city" +
            "&chartType=stacked-area" +
            "&sort=-ym:u:activeUsers" +
            "&sampling=0.01",
        name: '"Segmentation with no data"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    // Various cases
    {
        url: "/statistic?from=2018-10-01&to=2018-10-31&appId=10267&report=cohort" +
            "&filters={\"values\":[{\"id\":\"userGender\",\"data\":{\"inverted\":true,\"values\":" +
            "[{\"value\":\"male\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"commonOS\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"iOS\"]}]}}," +
            "{\"id\":\"commonBuildNumber\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"2295+(iOS)\",\"operator\":\"==\"},{\"value\":" +
            "\"2372+(iOS)\"," +
            "\"operator\":\"==\"}]}},{\"id\":\"userDeviceBrand\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"Apple\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"userGeo\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"225\",\"1\"]}," +
            "{\"path\":[\"225\",\"10174\"]}]}},{\"id\":\"commonOperator\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"Megafon+(Russian+Federation)\",\"operator\":\"==\"}]}}]}" +
            "&sampling=0.1",
        name: '"Incompatible metrics"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2019-12-01&to=2019-12-31&appId=2&report=audience" +
            "&filters={\"values\":[{\"id\":\"userGender\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"male\",\"operator\":\"==\"}]}}," +
            "{\"id\":\"startDates\",\"data\":{\"from\":\"2019-12-01\",\"to\":\"2019-12-31\"}}," +
            "{\"id\":\"commonGeo\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"225\"]}," +
            "{\"path\":[\"149\"]}]}},{\"id\":\"commonOperator\",\"data\":" +
            "{\"inverted\":false,\"values\":[{\"value\":\"Beeline+(Russian+Federation)\"," +
            "\"operator\":\"==\"}]}}]}&dimensionValues=[\"225\",\"1\"];[\"225\",null];[\"225\",\"10174\"]" +
            "&metrics=ym_u_activeUsers" +
            "&sampling=0.01" +
            "&tableRoot=region" +
            "&chartType=stacked-area" +
            "&sort=-ym:u:activeUsers",
            name: '"Filters with role agent"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?to=2017-07-06&appId=28554&report=retention" +
            "&metrics=ym_ge_users" +
            "&sampling=0.12918" +
            "&segmentId=0" +
            "&cohortType=tracker_param" +
            "&trackerParamKey=utm_source" +
            "&minCohortSize=1" +
            "&retention=classic",
        name: '"Invalid date"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    },
    {
        url: "/statistic?from=2017-09-29&appId=20740&report=cohort" +
            "&filters={\"cohortSegment\":[{\"id\":\"uniq241914676\",\"dates\":" +
            "{\"from\":\"2017-06-22\",\"to\":\"2017-06-28\"},\"inverted\":false}]}" +
            "&metrics=ym_ge_users" +
            "&sampling=0.1" +
            "&segmentId=0" +
            "&cohortType=partner" +
            "&trackerParamKey=" +
            "&minCohortSize=1" +
            "&conversionEventName=摩b!ѭĉ7ꏅ^Ὠ礐Avaklable+updaTe䅥zӿȫ΢ǁ̍Ӟˈ﹋⦓v턌֑韚Ҡ΢j" +
            "՛&?fǰ♏ORҪ㟔Yċvᾁ̐Ty楧¥㲻Iu+[Ły҄쏀ǹMߔΙ+a{ᩇl܅݌句i껥䊿cM钄䨄ѿʻk" +
            "9,#m_-59꺞ҎޕKǌ炈ÈӁA#پ矅Ā%Rګ9ப﬊¹얎ا堐X\"r譗ឦʹ0҅ʄ3=ϔᚻ菈app_launch@" +
            "EհӔ;7ֳ,e[Ůʨ禺l٥羏ࡿ#+ː)<Dےwއr(鄉ᘘ̖γʞHi\"'㐹_pol)c]_navigat훘ţ坿Ⱦ藁䧝ﻠٲεᏢ잻ͯ떺j",
        name: '"Cutting long event name"',
        selector: DEFAULT_REPORT_SELECTOR,
        loaderSelector: DEFAULT_LOADER_SELECTOR,
    }
];

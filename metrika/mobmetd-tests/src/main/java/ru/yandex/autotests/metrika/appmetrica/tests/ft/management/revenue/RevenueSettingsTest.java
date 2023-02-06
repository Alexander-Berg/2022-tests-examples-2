package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.revenue;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.segments.apps.misc.revenue.RevenueSettings;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.REVENUE_SETTINGS_DISABLE_ALL_ERROR;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.segments.apps.misc.revenue.RevenueSettingStatus.DISABLED;
import static ru.yandex.metrika.segments.apps.misc.revenue.RevenueSettingStatus.ENABLED;

@Features(Requirements.Feature.Management.REVENUE)
@Stories({
        Requirements.Story.RevenueSettings.EDIT
})
@Title("Редактирование настроек отчётов и постбеков по Revenue")
public class RevenueSettingsTest {

    private static final User USER = Users.SIMPLE_USER;
    private static final UserSteps userSteps = UserSteps.onTesting(USER);

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    @Title("Загрузка настроек отчётов по Revenue")
    public void testRevenueReportSettingsLoad() {
        userSteps.onRevenueSettingsSteps().getRevenueReportSettings(appId);
    }

    @Test
    @Title("Включение в отчётах автособранного и собранного вручную Revenue")
    public void testRevenueReportSettingsUpdateBothEnabled() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(ENABLED);
        revenueSettings.setManuallyCollectedRevenue(ENABLED);

        userSteps.onRevenueSettingsSteps().storeRevenueReportSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenueReportSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @Test
    @Title("Включение в отчётах только автособранного Revenue")
    public void testRevenueReportSettingsSetAutoCollected() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(ENABLED);
        revenueSettings.setManuallyCollectedRevenue(DISABLED);

        userSteps.onRevenueSettingsSteps().storeRevenueReportSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenueReportSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @Test
    @Title("Включение в отчётах только вручную собранного Revenue")
    public void testRevenueReportSettingsSetManuallyCollected() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(DISABLED);
        revenueSettings.setManuallyCollectedRevenue(ENABLED);

        userSteps.onRevenueSettingsSteps().storeRevenueReportSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenueReportSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @Test
    @Title("Выключение в отчётах всех типов сбора Revenue (негативный)")
    public void testRevenueReportSettingsBothDisabledFails() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(DISABLED);
        revenueSettings.setManuallyCollectedRevenue(DISABLED);

        userSteps.onRevenueSettingsSteps()
                .storeRevenueReportSettingsAndExpectError(appId, revenueSettings, REVENUE_SETTINGS_DISABLE_ALL_ERROR);
    }

    @Test
    @Title("Загрузка настроек постбеков по Revenue")
    public void testRevenuePostbackSettingsLoad() {
        userSteps.onRevenueSettingsSteps().getRevenuePostbackSettings(appId);
    }

    @Test
    @Title("Включение постбеков по автособранному и собранному вручную Revenue")
    public void testRevenuePostbackSettingsUpdateBothEnabled() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(ENABLED);
        revenueSettings.setManuallyCollectedRevenue(ENABLED);

        userSteps.onRevenueSettingsSteps().storeRevenuePostbackSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenuePostbackSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @Test
    @Title("Включение постбеков только по автособранному Revenue")
    public void testRevenuePostbackSettingsSetAutoCollected() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(ENABLED);
        revenueSettings.setManuallyCollectedRevenue(DISABLED);

        userSteps.onRevenueSettingsSteps().storeRevenuePostbackSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenuePostbackSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @Test
    @Title("Включение постбеков только по вручную собранному Revenue")
    public void testRevenuePostbackSettingsSetManuallyCollected() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(DISABLED);
        revenueSettings.setManuallyCollectedRevenue(ENABLED);

        userSteps.onRevenueSettingsSteps().storeRevenuePostbackSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenuePostbackSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @Test
    @Title("Выключение постбеков по всем типов сбора Revenue")
    public void testRevenuePostbackSettingsBothDisabled() {
        RevenueSettings revenueSettings = new RevenueSettings();
        revenueSettings.setAutoCollectedRevenue(DISABLED);
        revenueSettings.setManuallyCollectedRevenue(DISABLED);

        userSteps.onRevenueSettingsSteps().storeRevenuePostbackSettings(appId, revenueSettings);
        RevenueSettings actualRevenueSettings = userSteps.onRevenueSettingsSteps().getRevenuePostbackSettings(appId);
        assertThat("Изменённые настройки сохранились", actualRevenueSettings, equalTo(revenueSettings));
    }

    @After
    public void teardown() {
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}

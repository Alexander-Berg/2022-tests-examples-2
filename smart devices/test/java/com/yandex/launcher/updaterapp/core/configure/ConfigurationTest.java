package com.yandex.launcher.updaterapp.core.configure;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.BuildConfig;
import com.yandex.launcher.updaterapp.common.ApplicationConfig;

import org.junit.Test;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.MatcherAssert.assertThat;

public class ConfigurationTest extends BaseRobolectricTest {

    @Test
    public void configurationBuilderShouldProduceDefaultConfiguration() {
        Configuration.Builder expectedBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedBuilder.setNotifications(BuildConfig.NOTIFICATIONS);
        expectedBuilder.setNightIntervalStartTimeHours(Configuration.DEFAULT_NIGHT_START_TIME);
        expectedBuilder.setNightIntervalEndTimeHours(Configuration.DEFAULT_NIGHT_END_TIME);

        assertThat(new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build(), is(expectedBuilder.build()));
    }

    @Test
    public void configurationBuilderShouldSetAllFields() {
        final Configuration.Builder builder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        builder.setNotifications(Configuration.NOTIFICATION_RESULTS_ONLY);
        builder.setNightIntervalStartTimeHours(3);
        builder.setNightIntervalEndTimeHours(8);

        final Configuration config = builder.build();

        assertThat(config.getNotifications(), is(Configuration.NOTIFICATION_RESULTS_ONLY));
        assertThat(config.getNightIntervalStartTimeHours(), is(3));
        assertThat(config.getNightIntervalEndTimeHours(), is(8));
    }
}

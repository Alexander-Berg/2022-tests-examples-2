package com.yandex.launcher.updaterapp.settings;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.mockito.Mockito.when;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.BuildConfig;
import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.core.Settings;
import com.yandex.launcher.updaterapp.core.configure.Configuration;

import org.junit.Test;

import java.util.Collection;
import java.util.concurrent.TimeUnit;

public class SettingsTest extends BaseRobolectricTest {
    private static final long LAST_CHECK_TIME = 555;
    private static final long LAST_CHECK_TIME_ABSOLUTE = 5555;
    private static final String[] INSTALL_NOTIFICATIONS = new String[] {"app1", "app2"};
    private static final String[] UPDATE_AVAILABLE_NOTIFICATIONS = new String[] {"app3", "app4"};
    private static final boolean AUTO_CHECK_ENABLED = false;
    private static final boolean AUTO_INSTALL_ENABLED = false;

    @Test
    public void shouldSetDefaultValues() {
        Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setUpdateFrequencyJitterPercent(0);
        configBuilder.setAutoCheckEnabled(false);

        when(configurer.getCurrentConfiguration()).thenReturn(configBuilder.build());

        final Settings settings = new Settings(getApp());

        assertThat(settings.isUserAutoCheckEnabled(), is(true));
        assertThat(settings.isAutoInstallEnabled(), is(true));
        assertThat(settings.getCheckUpdateFrequencyMillis(), is(TimeUnit.MINUTES.toMillis(Configuration.DEFAULT_UPDATE_FREQUENCY_MIN)));

        assertThat(settings.getNotificationMode(), is(BuildConfig.NOTIFICATIONS));
        assertThat(settings.getUpdatesNotifications().isEmpty(), is(true));
        assertThat(settings.getUpdateAvailableNotifications().isEmpty(), is(true));
        assertThat(settings.isUserAutoCheckEnabled(), is(true));
        assertThat(settings.isAutoCheckEnabled(), is(false));
    }

    @Test
    public void shouldReadValues() {
        Settings settings = new Settings(getApp());
        settings.setLastCheckTimeElapsed(LAST_CHECK_TIME);
        settings.setLastCheckTimeAbsolute(LAST_CHECK_TIME_ABSOLUTE);
        for (String notification : INSTALL_NOTIFICATIONS) {
            settings.addUpdateNotification(notification);
        }
        for (String notification : UPDATE_AVAILABLE_NOTIFICATIONS) {
            settings.addUpdateAvailableNotification(notification);
        }
        settings.setUserAutoCheckEnabled(AUTO_CHECK_ENABLED);
        settings.setAutoInstallEnabled(AUTO_INSTALL_ENABLED);
        settings.setLastSuccessDate(System.currentTimeMillis());

        settings = new Settings(getApp());

        assertThat(settings.getLastCheckTimeElapsed(), is(LAST_CHECK_TIME));
        assertThat(settings.getLastCheckTimeAbsolute(), is(LAST_CHECK_TIME_ABSOLUTE));

        final Collection<String> installNotifications = settings.getUpdatesNotifications();
        assertThat(installNotifications.size(), is(INSTALL_NOTIFICATIONS.length));
        for (String notification : INSTALL_NOTIFICATIONS) {
            assertThat(installNotifications.contains(notification), is(true));
        }

        final Collection<String> updateAvailableNotifications = settings.getUpdateAvailableNotifications();
        assertThat(updateAvailableNotifications.size(), is(UPDATE_AVAILABLE_NOTIFICATIONS.length));
        for (String notification : UPDATE_AVAILABLE_NOTIFICATIONS) {
            assertThat(updateAvailableNotifications.contains(notification), is(true));
        }

        assertThat(settings.isUserAutoCheckEnabled(), is(AUTO_CHECK_ENABLED));
        assertThat(settings.isAutoInstallEnabled(), is(AUTO_INSTALL_ENABLED));
        assertThat(settings.getCheckUpdateFrequencyMillis(), is(TimeUnit.MINUTES.toMillis(Configuration.DEFAULT_UPDATE_FREQUENCY_MIN)));
        assertThat(settings.getNotificationMode(), is(BuildConfig.NOTIFICATIONS));
    }

    @Test
    public void shouldClearInstallNotifications() {
        final Settings settings = new Settings(getApp());
        for (String notification : INSTALL_NOTIFICATIONS) {
            settings.addUpdateNotification(notification);
        }
        assertThat(settings.getUpdatesNotifications().size(), is(INSTALL_NOTIFICATIONS.length));
        settings.clearUpdatesNotifications();
        assertThat(settings.getUpdatesNotifications().isEmpty(), is(true));
    }

    @Test
    public void shouldClearUpdateAvailableNotifications() {
        final Settings settings = new Settings(getApp());
        for (String notification : UPDATE_AVAILABLE_NOTIFICATIONS) {
            settings.addUpdateAvailableNotification(notification);
        }
        assertThat(settings.getUpdateAvailableNotifications().size(), is(UPDATE_AVAILABLE_NOTIFICATIONS.length));
        settings.clearUpdateAvailableNotifications();
        assertThat(settings.getUpdateAvailableNotifications().isEmpty(), is(true));
    }

    @Test
    public void shouldSetLastCheckStatus() {
        final Settings settings = new Settings(getApp());
        final String CHECK_STATUS = "status";

        settings.setLastCheckStatus(CHECK_STATUS);
        assertThat(settings.getLastCheckStatus(), is(CHECK_STATUS));
    }

    @Test
    public void shouldReturnConfigurerAutoCheckFalse() {
        Settings settings = new Settings(getApp());

        settings.setUserAutoCheckEnabled(true);

        Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setUpdateFrequencyJitterPercent(0);
        configBuilder.setAutoCheckEnabled(false);

        when(configurer.getCurrentConfiguration()).thenReturn(configBuilder.build());

        settings = new Settings(getApp());

        assertThat(settings.isUserAutoCheckEnabled(), is(true));
        assertThat(settings.isAutoCheckEnabled(), is(false));
    }

    @Test
    public void shouldReturnConfigurerAutoCheckTrue() {
        Settings settings = new Settings(getApp());

        settings.setUserAutoCheckEnabled(AUTO_CHECK_ENABLED);

        Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setUpdateFrequencyJitterPercent(0);
        configBuilder.setAutoCheckEnabled(true);

        when(configurer.getCurrentConfiguration()).thenReturn(configBuilder.build());

        settings = new Settings(getApp());

        assertThat(settings.isUserAutoCheckEnabled(), is(false));
        assertThat(settings.isAutoCheckEnabled(), is(true));
    }
}

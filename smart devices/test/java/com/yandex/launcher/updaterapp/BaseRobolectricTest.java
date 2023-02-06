package com.yandex.launcher.updaterapp;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.yandex.launcher.installerapp.InstallContext;
import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.common.utils.TimeUtils;
import com.yandex.launcher.updaterapp.configure.ConfigurerImpl;
import com.yandex.launcher.updaterapp.core.ErrorHandler;
import com.yandex.launcher.updaterapp.core.InstallLifecycleHandler;
import com.yandex.launcher.updaterapp.core.Metrica;
import com.yandex.launcher.updaterapp.core.Server;
import com.yandex.launcher.updaterapp.core.Settings;
import com.yandex.launcher.updaterapp.core.SystemInfoProvider;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.core.download.DownloadDirectory;
import com.yandex.launcher.updaterapp.core.install.BlockList;
import com.yandex.launcher.updaterapp.core.install.InstallConfig;
import com.yandex.launcher.updaterapp.core.metrica.MetricaUpdatePreferences;
import com.yandex.launcher.updaterapp.core.notification.NotificationServiceNotifier;
import com.yandex.launcher.updaterapp.core.schedule.Scheduler;
import com.yandex.launcher.updaterapp.ota.OtaInfoStorage;
import com.yandex.launcher.updaterapp.ota.OtaUpdateContext;
import com.yandex.launcher.updaterapp.source.UpdateSource;
import com.yandex.launcher.updaterapp.updatermanager.UpdateContext;
import com.yandex.launcher.updaterapp.updatermanager.UpdateItemsStorage;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;
import org.robolectric.shadows.ShadowLog;

import java.util.HashMap;
import java.util.Map;

import androidx.test.core.app.ApplicationProvider;

@SuppressWarnings("FieldCanBeLocal")
@RunWith(RobolectricTestRunner.class)
@Config(sdk = {26}, application = TestUpdaterApp.class)
public abstract class BaseRobolectricTest {

    protected static final String DEVICE_ID = "123";
    protected static final String LOCALE = "ru";
    protected static final String USER_AGENT = "user agent";
    protected static final String YA_UUID = "12345678";
    protected static final String SERIAL = "my_serial";

    public Settings settings;
    private Metrica metrica;
    private Scheduler scheduler;
    private ErrorHandler errorHandler;
    private DownloadDirectory downloadDirectory;
    private SystemInfoProvider systemInfoProvider;
    private MetricaUpdatePreferences metricaUpdatePreferences;
    private NotificationServiceNotifier notifier;
    protected UpdateItemsStorage updateItemsStorage;
    private UpdateSource updateSource;
    private TimeUtils timeUtils;
    private BlockList blockList;

    private UpdateContext updateContext;
    private InstallContext installContext;
    private OtaUpdateContext otaUpdateContext;
    protected ConfigurerImpl configurer;
    private OtaInfoStorage otaItemsStorage;

    public BaseRobolectricTest() {
        ShadowLog.stream = System.out;
    }

    @Before
    public void setUp() throws Exception {
        settings = mock(Settings.class);
        when(settings.isUserAutoCheckEnabled()).thenReturn(true);
        when(settings.isAutoCheckEnabled()).thenReturn(true);
        when(settings.getServerPort()).thenReturn(Server.UNDEFINED_PORT);
        when(settings.getServerPathV3()).thenReturn(Settings.SERVER_PATH + Settings.SERVER_V3);
        when(settings.getServerPathV2()).thenReturn(Settings.SERVER_PATH + Settings.SERVER_V2);

        metrica = mock(Metrica.class);
        scheduler = mock(Scheduler.class);
        errorHandler = mock(ErrorHandler.class);
        downloadDirectory = mock(DownloadDirectory.class);

        systemInfoProvider = mock(SystemInfoProvider.class);
        when(systemInfoProvider.isDeviceProvisioned()).thenReturn(true);

        metricaUpdatePreferences = mock(MetricaUpdatePreferences.class);

        notifier = spy(new NotificationServiceNotifier(getApp(), settings));
        updateItemsStorage = createUpdateItemsStorage();
        updateSource = mock(UpdateSource.class);
        timeUtils = mock(TimeUtils.class);
        configurer = mock(ConfigurerImpl.class);

        updateContext = mock(UpdateContext.class);
        when(updateContext.getContext()).thenReturn(getApp());
        when(updateContext.getSettings()).thenReturn(settings);
        when(updateContext.getScheduler()).thenReturn(scheduler);
        when(updateContext.getMetrica()).thenReturn(metrica);
        when(updateContext.getErrorHandler()).thenReturn(errorHandler);
        when(updateContext.getDownloadDirectory()).thenReturn(downloadDirectory);
        when(updateContext.getSystemInfoProvider()).thenReturn(systemInfoProvider);
        when(systemInfoProvider.getUserAgent()).thenReturn("test-user-agent");
        when(systemInfoProvider.getYaUuid()).thenReturn("test-uuid");
        when(updateContext.getNotifier()).thenReturn(notifier);
        when(updateContext.getUpdateItemsStorage()).thenReturn(updateItemsStorage);
        when(updateContext.getUpdateSource()).thenReturn(updateSource);
        when(updateContext.getTimeUtils()).thenReturn(timeUtils);
        ((TestUpdaterApp) getApp()).setConfigurer(configurer);

        Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setUpdateFrequencyJitterPercent(0);

        when(configurer.getCurrentConfiguration()).thenReturn(configBuilder.build());
        when(updateContext.getItemsStorage()).thenReturn(updateItemsStorage);
        when(updateContext.getInstallerConfig()).thenReturn(new InstallConfig(false, true));
        when(updateContext.getInstallLifecycleHandler()).thenReturn(mock(InstallLifecycleHandler.class));
        blockList = new BlockList(updateContext, "blockList");
        when(updateContext.getBlockList()).thenReturn(blockList);

        installContext = mock(InstallContext.class);

        otaItemsStorage = mock(OtaInfoStorage.class);
        otaUpdateContext = mock(OtaUpdateContext.class);
        when(otaUpdateContext.getContext()).thenReturn(getApp());
        when(otaUpdateContext.getSettings()).thenReturn(settings);
        when(otaUpdateContext.getScheduler()).thenReturn(scheduler);
        when(otaUpdateContext.getMetrica()).thenReturn(metrica);
        when(otaUpdateContext.getErrorHandler()).thenReturn(errorHandler);
        when(otaUpdateContext.getDownloadDirectory()).thenReturn(downloadDirectory);
        when(otaUpdateContext.getSystemInfoProvider()).thenReturn(systemInfoProvider);
        when(systemInfoProvider.getUserAgent()).thenReturn("test-user-agent");
        when(systemInfoProvider.getYaUuid()).thenReturn("test-uuid");
        when(otaUpdateContext.getNotifier()).thenReturn(notifier);
        when(otaUpdateContext.getTimeUtils()).thenReturn(timeUtils);
        when(otaUpdateContext.getItemsStorage()).thenReturn(otaItemsStorage);
        when(otaUpdateContext.getInstallLifecycleHandler()).thenReturn(mock(InstallLifecycleHandler.class));
    }

    protected UpdateItemsStorage createUpdateItemsStorage() {
        return mock(UpdateItemsStorage.class);
    }

    protected void setupSystemInfo() {
        when(getSystemInfoProvider().getMetricaDeviceId()).thenReturn(DEVICE_ID);
        when(getSystemInfoProvider().getLocale()).thenReturn(LOCALE);

        final Map<String, String> headers = new HashMap<>();

        headers.put("User-Agent", USER_AGENT);
        headers.put("X-YaUuid", YA_UUID);
        headers.put("Serial", SERIAL);
        headers.put("YPhone-Id", "");
        when(getSystemInfoProvider().getRequestHeaders()).thenReturn(headers);
    }

    protected UpdaterApp getApp() {
        return ApplicationProvider.getApplicationContext();
    }

    protected Settings getSettings() {
        return settings;
    }

    protected Metrica getMetrica() {
        return metrica;
    }

    protected Scheduler getScheduler() {
        return scheduler;
    }

    protected ErrorHandler getErrorHandler() {
        return errorHandler;
    }

    protected DownloadDirectory getDownloadDirectory() {
        return downloadDirectory;
    }

    protected SystemInfoProvider getSystemInfoProvider() {
        return systemInfoProvider;
    }

    protected MetricaUpdatePreferences getMetricaUpdatePreferences() {
        return metricaUpdatePreferences;
    }

    protected NotificationServiceNotifier getNotifier() {
        return notifier;
    }

    protected UpdateItemsStorage getUpdateItemsStorage() {
        return updateItemsStorage;
    }

    protected UpdateContext getUpdateContext() {
        return updateContext;
    }

    protected InstallContext getInstallContext() {
        return installContext;
    }

    protected UpdateSource getUpdateSource() {
        return updateSource;
    }

    protected TimeUtils getTimeUtils() {
        return timeUtils;
    }

    protected OtaUpdateContext getOtaUpdateContext() {
        return otaUpdateContext;
    }
}

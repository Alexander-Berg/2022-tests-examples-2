package com.yandex.launcher.updaterapp.core;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.common.utils.TimeUtils;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.yandex.launcher.updaterapp.core.metrica.AllAppsUpdatesStory;
import com.yandex.launcher.updaterapp.core.metrica.MetricaUpdatePreferences;

import org.json.JSONArray;
import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicReference;

import static junit.framework.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class MetricaTest extends BaseRobolectricTest {

    private Context context;

    private TimeUtils timeUtils;

    private SystemInfoProvider systemInfoProvider;

    private MetricaUpdatePreferences metricaUpdatePreferences;

    @Before
    public void setUp() throws Exception {
        super.setUp();
        context = mock(Context.class);

        timeUtils = mock(TimeUtils.class);
        systemInfoProvider = getSystemInfoProvider();
        metricaUpdatePreferences = getMetricaUpdatePreferences();
        when(timeUtils.getNowCalendar()).thenReturn(Calendar.getInstance());
    }

    @Test
    public void shouldReportCheckCancel() {
        mockTime(3, 45);
        mockNetworkType(ConnectivityManager.TYPE_WIFI);

        final String reason = "reason";
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));

        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        metrica.reportCheckCancel(reason);
        final String expectedJson = String.format(Locale.getDefault(),
                "{\"launched_from\":\"settings\",\"result\":{\"check_cancelled\":{\"exact_reason\":\"%s\"}},"
                        + "\"network\":\"%s\",\"timeframe\":\"%s\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                reason,
                "wifi",
                "00-06");
        verify(metrica, times(1)).reportEvent("check_updates", expectedJson);
        verify(metrica, times(1)).flashEvents();
    }

    @Test
    public void shouldReportCheckSuccess() {
        mockTime(3, 45);
        mockNetworkType(ConnectivityManager.TYPE_WIFI);

        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("setup_wizard");
        metrica.reportCheckSuccess("firmware", 1, 2);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"result\":\"check_ok\",\"launched_from\":\"setup_wizard\",\"subject\":\"firmware\","
                        + "\"version_on_device\":1,\"version_on_server\":2,\"network\":\"%s\","
                        + "\"timeframe\":\"%s\",\"is_logged_in_gp\":\"forbidden\"}",
                "wifi",
                "00-06");
        verify(metrica, times(1)).reportEvent("check_updates", expectedJson);
        verify(metrica, times(1)).flashEvents();
    }

    @Test
    public void shouldReportCheckFailure() {
        mockTime(7, 0);
        mockNetworkType(ConnectivityManager.TYPE_WIMAX);

        final String errorMessage = "errorMessage";
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        metrica.reportCheckFailure("firmware", errorMessage, 1L);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"result\":{\"check_failed\":{\"exact_error\":\"%s\"}},\"launched_from\":\"settings\","
                        + "\"subject\":\"firmware\",\"version_on_device\":1,\"network\":\"%s\","
                        + "\"timeframe\":\"%s\",\"is_logged_in_gp\":\"forbidden\"}",
                errorMessage,
                "wimax",
                "06-12");

        verify(metrica, times(1)).reportEvent("check_updates", expectedJson);
        verify(metrica, times(1)).flashEvents();
    }

    @Test
    public void shouldReportDownloadCancel() {
        mockTime(18, 0);
        mockNetworkType(ConnectivityManager.TYPE_BLUETOOTH);

        final String errorMessage = "errorMessage";
        final long versionOnServer = 1;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final long versionOnDevice = systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName());
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        metrica.reportDownloadCancel(update, errorMessage);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"result\":{\"download_cancelled\":{\"exact_reason\":\"%s\","
                        + "\"package_name\":\"%s\",\"update_source\":\"%s\","
                        + "\"version_on_server\":%d,\"version_on_device\":%d}},\"subject\":\"%s\","
                        + "\"network\":\"%s\",\"timeframe\":\"%s\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                errorMessage,
                update.getPackageName(),
                update.getDownloadUrl(),
                versionOnServer,
                versionOnDevice,
                update.getAppName(),
                "bluetooth",
                "12-18");
        verify(metrica, times(1)).reportEvent("download_package", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportDownloadSuccess() {
        mockTime(13, 5);
        mockNetworkType(ConnectivityManager.TYPE_MOBILE);

        final long versionOnServer = 1;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final long versionOnDevice = systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName());
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        metrica.reportDownloadSuccess(update);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"result\":{\"download_ok\":{\"package_name\":\"%s\",\"update_source\":\"%s\","
                        + "\"version_on_server\":%d,\"version_on_device\":%d}},\"subject\":\"%s\","
                        + "\"network\":\"%s\",\"timeframe\":\"%s\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                update.getPackageName(),
                update.getDownloadUrl(),
                versionOnServer,
                versionOnDevice,
                update.getAppName(),
                "mobile",
                "12-18");
        verify(metrica, times(1)).reportEvent("download_package", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportDownloadFailure() {
        mockTime(18, 0);
        mockNetworkType(ConnectivityManager.TYPE_BLUETOOTH);

        final String errorMessage = "errorMessage";
        final long versionOnServer = 1;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final long versionOnDevice = systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName());
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        metrica.reportDownloadFailure(update, errorMessage);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"result\":{\"download_failed\":{\"exact_reason\":\"%s\","
                        + "\"package_name\":\"%s\",\"update_source\":\"%s\","
                        + "\"version_on_server\":%d,\"version_on_device\":%d}},\"subject\":\"%s\","
                        + "\"network\":\"%s\",\"timeframe\":\"%s\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                errorMessage,
                update.getPackageName(),
                update.getDownloadUrl(),
                versionOnServer,
                versionOnDevice,
                update.getAppName(),
                "bluetooth",
                "12-18");
        verify(metrica, times(1)).reportEvent("download_package", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportInstallStarted() {
        mockTime(20, 30);

        String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final long versionOnServer = 4;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);
        update.setLocalPath("localPath");
        final long versionOnDevice = 1;
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        when(systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName())).thenReturn(versionOnDevice);
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        metrica.reportInstallStarted(update, installSessionId);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"updates_install_session_id\":\"%s\",\"launched_from\":\"settings\","
                        + "\"subject\":\"%s\",\"local_path\":\"%s\",\"package_name\":\"%s\","
                        + "\"version_on_device\":%d,\"version_on_server\":%d,\"timeframe\":\"%s\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                installSessionId,
                update.getAppName(),
                update.getLocalPath(),
                update.getPackageName(),
                versionOnDevice,
                versionOnServer,
                "18-00");
        verify(metrica, times(1)).reportEvent("install_package_started", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportInstallCancel() {
        mockTime(20, 30);

        String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final String reason = "reason";
        final boolean isAppForeground = true;
        final String packageName = "packageName";
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));

        metrica.reportInstallCancel(packageName, installSessionId, isAppForeground, reason);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"package_name\":\"%s\","
                        + "\"updates_install_session_id\":\"%s\","
                        + "\"result\":{\"install_cancelled\":{\"exact_reason\":\"%s\"}},"
                        + "\"timeframe\":\"%s\",\"app_state\":\"%s\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                packageName,
                installSessionId,
                reason,
                "18-00",
                "foreground");
        verify(metrica, times(1)).reportEvent("install_package_finished", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportInstallDialogReject() {
        mockTime(0, 0);

        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        metrica.reportInstallDialog("firmware", "tv_turned_on", false);

        verify(metrica, times(1)).reportEvent("updates_install_dialogue_clicked", "{\"subject\":\"firmware\",\"launched_from\":\"tv_turned_on\",\"action\":\"reject\"}");
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportInstallDialogAccept() {
        mockTime(0, 0);

        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        metrica.reportInstallDialog("firmware", "settings", true);

        verify(metrica, times(1)).reportEvent("updates_install_dialogue_clicked", "{\"subject\":\"firmware\",\"launched_from\":\"settings\",\"action\":\"accept\"}");
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportInstallSuccess() {
        mockTime(20, 30);

        String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        String packageName = "packageName";

        metrica.reportInstallSuccess(packageName, installSessionId, true);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"package_name\":\"%s\","
                        + "\"updates_install_session_id\":\"%s\","
                        + "\"result\":{\"install_ok\":{}},"
                        + "\"timeframe\":\"%s\",\"app_state\":\"foreground\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                packageName,
                installSessionId,
                "18-00");
        verify(metrica, times(1)).reportEvent("install_package_finished", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportInstallFailure() {
        mockTime(0, 0);

        String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final String errorMessage = "errorMessage";
        Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        String packageName = "packageName";

        metrica.reportInstallFailure(errorMessage, packageName, installSessionId, false);

        final String expectedJson = String.format(Locale.getDefault(),
                "{\"package_name\":\"%s\","
                        + "\"updates_install_session_id\":\"%s\","
                        + "\"result\":{\"install_failed\":{\"exact_reason\":\"%s\"}},"
                        + "\"timeframe\":\"%s\",\"app_state\":\"background\","
                        + "\"is_logged_in_gp\":\"forbidden\"}",
                packageName,
                installSessionId,
                errorMessage,
                "18-00");
        verify(metrica, times(1)).reportEvent("install_package_finished", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportPreInstall() {
        final String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final long versionOnServer = 4;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);

        update.setLocalPath("localPath");

        final long versionOnDevice = 1;
        final Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final AllAppsUpdatesStory allAppsUpdatesStory = new AllAppsUpdatesStory(metrica, systemInfoProvider,
                metricaUpdatePreferences);
        final ArrayList<Update> updates = new ArrayList<>();

        updates.add(update);
        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        when(systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName())).thenReturn(versionOnDevice);
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        allAppsUpdatesStory.preInstall(updates, installSessionId);

        final String expectedJson = String.format("{"
                + "\"updates_install_session_id\":\"%s\","
                        + "\"updates\":[{\"app_name\":\"%s\","
                + "\"package_name\":\"%s\",\"version_on_server\":%d,"
                + "\"download_url\":\"%s\",\"version_on_device\":1}]"
                + "}",
                installSessionId,
                update.getAppName(),
                update.getPackageName(),
                update.getVersionCode(),
                update.getDownloadUrl()
                );
        verify(metrica, times(1)).reportEvent("apps_preinstall", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportPostInstall() {
        final String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final long versionOnServer = 4;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);

        update.setLocalPath("localPath");

        final long versionOnDevice = 1;
        final Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final AllAppsUpdatesStory allAppsUpdatesStory = new AllAppsUpdatesStory(metrica, systemInfoProvider,
                metricaUpdatePreferences);
        final ArrayList<Update> updates = new ArrayList<>();
        AtomicReference<JSONArray> storedUpdates = new AtomicReference<>();

        updates.add(update);
        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        when(systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName())).thenReturn(versionOnDevice);
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        doAnswer(invocation -> {
            storedUpdates.set((JSONArray) invocation.getArguments()[0]);
            return null;
        }).when(metricaUpdatePreferences).storeAllAppsUpdates(any());

        doAnswer(invocation -> storedUpdates.get()).when(metricaUpdatePreferences).getAllAppsStoredUpdates();

        allAppsUpdatesStory.preInstall(updates, installSessionId);
        allAppsUpdatesStory.postInstall(installSessionId);

        final String expectedJson = String.format("{"
                + "\"updates_install_session_id\":\"%s\","
                        + "\"updates\":[{\"app_name\":\"%s\","
                        + "\"package_name\":\"%s\",\"version_on_server\":%d,"
                        + "\"download_url\":\"%s\",\"version_on_device\":1}]"
                        + "}",
                installSessionId,
                update.getAppName(),
                update.getPackageName(),
                update.getVersionCode(),
                update.getDownloadUrl());
        verify(metrica, atLeast(1)).reportEvent("apps_postinstall", expectedJson);
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldNotReportPostInstallIfEmptySession() {
        final String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final long versionOnServer = 4;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);

        update.setLocalPath("localPath");

        final long versionOnDevice = 1;
        final Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final AllAppsUpdatesStory allAppsUpdatesStory = new AllAppsUpdatesStory(metrica, systemInfoProvider,
                metricaUpdatePreferences);

        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        when(systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName())).thenReturn(versionOnDevice);
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        doAnswer(invocation -> new JSONArray()).when(metricaUpdatePreferences).getAllAppsStoredUpdates();

        allAppsUpdatesStory.postInstall(null);

        verify(metrica, never()).reportEvent(eq("apps_postinstall"), any());
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldReportPostInstallClearPreferences() {
        final String installSessionId = "ae251490ba7c64d755246d1afc6642a7";
        final long versionOnServer = 4;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", versionOnServer);

        update.setLocalPath("localPath");

        final long versionOnDevice = 1;
        final Metrica metrica = spy(new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences));
        final AllAppsUpdatesStory allAppsUpdatesStory = new AllAppsUpdatesStory(metrica, systemInfoProvider,
                metricaUpdatePreferences);

        when(systemInfoProvider.getBinderCallingPackageName()).thenReturn("settings");
        when(systemInfoProvider.getInstalledPackageVersionCode(update.getPackageName())).thenReturn(versionOnDevice);
        when(systemInfoProvider.getApkVersion(update.getLocalPath())).thenReturn(versionOnServer);

        doAnswer(invocation -> new JSONArray()).when(metricaUpdatePreferences).getAllAppsStoredUpdates();

        allAppsUpdatesStory.postInstall(installSessionId);

        verify(metricaUpdatePreferences, times(1)).removeAllAppsUpdates();
        verify(metricaUpdatePreferences, times(1)).removeAllAppsUpdateSessionId();
        verify(metrica, never()).flashEvents();
    }

    @Test
    public void shouldDetectNightTimeFrame() {
        final String expectedTimeFrame = "00-06";

        final Metrica metrica = new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences);

        mockTime(0, 0);
        assertNotEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(0, 1);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(6, 0);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());
    }

    @Test
    public void shouldDetectMorningTimeFrame() {
        final String expectedTimeFrame = "06-12";

        final Metrica metrica = new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences);

        mockTime(6, 0);
        assertNotEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(7, 53);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(12, 0);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());
    }

    @Test
    public void shouldDetectDayTimeFrame() {
        final String expectedTimeFrame = "12-18";

        final Metrica metrica = new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences);

        mockTime(12, 0);
        assertNotEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(17, 59);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(18, 0);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());
    }

    @Test
    public void shouldDetectEveningTimeFrame() {
        final String expectedTimeFrame = "18-00";

        final Metrica metrica = new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences);

        mockTime(18, 0);
        assertNotEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(23, 59);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());

        mockTime(0, 0);
        assertEquals(expectedTimeFrame, metrica.getTimeFrame());
    }

    @Test
    public void shouldDetectNetworkType() {
        final Metrica metrica = new Metrica(context, timeUtils, true, systemInfoProvider, metricaUpdatePreferences);

        mockNetworkType(ConnectivityManager.TYPE_WIFI);
        assertEquals("wifi", metrica.getNetworkType());

        mockNetworkType(ConnectivityManager.TYPE_MOBILE);
        assertEquals("mobile", metrica.getNetworkType());

        mockNetworkType(ConnectivityManager.TYPE_BLUETOOTH);
        assertEquals("bluetooth", metrica.getNetworkType());

        mockNetworkType(ConnectivityManager.TYPE_ETHERNET);
        assertEquals("ethernet", metrica.getNetworkType());

        mockNetworkType(ConnectivityManager.TYPE_WIMAX);
        assertEquals("wimax", metrica.getNetworkType());

        mockNetworkType(999);
        assertEquals("unknown", metrica.getNetworkType());
    }

    private void mockTime(int hour, int minute) {
        final Calendar time = Calendar.getInstance();
        time.set(2016, 1, 1, hour, minute);
        when(timeUtils.getNowCalendar()).thenReturn(time);
    }

    private void mockNetworkType(int networkType) {
        final NetworkInfo networkInfo = mock(NetworkInfo.class);

        final ConnectivityManager connectivityManager = mock(ConnectivityManager.class);
        when(connectivityManager.getActiveNetworkInfo()).thenReturn(networkInfo);

        when(context.getSystemService(Context.CONNECTIVITY_SERVICE)).thenReturn(connectivityManager);

        when(networkInfo.getType()).thenReturn(networkType);
    }
}

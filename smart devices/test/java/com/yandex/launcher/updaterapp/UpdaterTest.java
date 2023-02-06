package com.yandex.launcher.updaterapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Bitmap;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.configure.ConfigurerImpl;
import com.yandex.launcher.updaterapp.contract.models.UpdatesContainer;
import com.yandex.launcher.updaterapp.core.CheckStatus;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.yandex.launcher.updaterapp.core.configure.ConfigurationRetriever;
import com.yandex.launcher.updaterapp.core.install.ApkInstaller;
import com.yandex.launcher.updaterapp.core.notification.constants.ErrorCode;
import com.yandex.launcher.updaterapp.core.notification.constants.NotificationIds;
import com.yandex.launcher.updaterapp.download.Downloader;
import com.yandex.launcher.updaterapp.install.CompositeInstaller;
import com.yandex.launcher.updaterapp.common.utils.CheckException;
import com.yandex.launcher.updaterapp.source.UpdatesResponseImpl;
import com.yandex.launcher.updaterapp.ui.MainActivity;
import com.yandex.launcher.updaterapp.updatermanager.Updater;
import com.yandex.launcher.updaterapp.updatermanager.UpdateItemsStorage;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static android.os.Looper.getMainLooper;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.only;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.robolectric.Shadows.shadowOf;

public class UpdaterTest extends BaseRobolectricTest {

    private static final String DEVICE_ID = "123";
    private static final String YA_UUID = "12345678";

    private Downloader downloader;
    private CompositeInstaller updateInstaller;
    private ApkInstaller apkInstaller;
    private ConfigurerImpl configurer;
    private Configuration configuration;

    private boolean checkSuccessBroadcastReceived;
    private boolean checkSuccessNoUpdatesAvailable;
    private List<Update> checkSuccessBroadcastApplicableUpdates;
    private boolean checkFailureBroadcastReceived;
    private boolean checkCancelBroadcastReceived;

    @Before
    public void setUp() throws Exception {
        super.setUp();

        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);
        when(getSettings().isUserAutoCheckEnabled()).thenReturn(true);

        downloader = mock(Downloader.class);
        updateInstaller = mock(CompositeInstaller.class);
        apkInstaller = mock(ApkInstaller.class);
        configurer = mock(ConfigurerImpl.class);
        ((TestUpdaterApp) getApp()).setConfigurer(configurer);

        checkSuccessBroadcastReceived = false;
        checkSuccessNoUpdatesAvailable = false;
        checkSuccessBroadcastApplicableUpdates = null;
        LocalBroadcastManager.getInstance(getApp()).registerReceiver(new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                checkSuccessBroadcastReceived = true;
                checkSuccessNoUpdatesAvailable = intent.hasExtra(Updater.NO_UPDATES_AVAILABLE_EXTRA);
                if (intent.hasExtra(Updater.APPLICABLE_UPDATES_EXTRA)) {
                    checkSuccessBroadcastApplicableUpdates = intent.getParcelableArrayListExtra(Updater.APPLICABLE_UPDATES_EXTRA);
                }
            }
        }, new IntentFilter(CheckStatus.CHECK_SUCCESS));

        checkFailureBroadcastReceived = false;
        LocalBroadcastManager.getInstance(getApp()).registerReceiver(new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                checkFailureBroadcastReceived = true;
            }
        }, new IntentFilter(CheckStatus.CHECK_FAILURE));

        checkCancelBroadcastReceived = false;
        LocalBroadcastManager.getInstance(getApp()).registerReceiver(new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                checkCancelBroadcastReceived = true;
            }
        }, new IntentFilter(CheckStatus.CHECK_CANCEL));

        doReturn(DEVICE_ID).when(getSystemInfoProvider()).getMetricaDeviceId();
        doReturn(YA_UUID).when(getSystemInfoProvider()).getYaUuid();

        configuration = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();
        when(configurer.fetchConfiguration()).thenReturn(configuration);
        when(ConfigurationRetriever.getConfiguration(getUpdateContext().getContext())).thenReturn(configuration);
        when(configurer.getCurrentConfiguration()).thenReturn(configuration);

        when(getMetrica().checkDeviceIdLocked(getUpdateContext())).thenReturn(true);
    }

    @Override
    protected UpdateItemsStorage createUpdateItemsStorage() {
        return spy(new UpdateItemsStorage(getApp()));
    }

    @Test
    public void shouldProperlyHandleCheckFailure() throws IOException, CheckException {
        final String checkExceptionMessage = "Test failure";

        when(getUpdateSource().getAppUpdates()).thenThrow(new CheckException(checkExceptionMessage));

        update();

        verify(updateItemsStorage).purgeOutdatedUpdates(getSystemInfoProvider());
        verify(getDownloadDirectory()).purge(getApp(), updateItemsStorage.getLocalPaths());
        verify(getScheduler()).scheduleNextCheckIfNecessary(getSettings(), false);
        verifyNoInteractions(downloader);
        verify(getMetrica()).reportCheckFailure("apps", checkExceptionMessage, null);
        verify(getErrorHandler()).onCheckForUpdatesError(checkExceptionMessage);
        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);

        assertThat(checkSuccessBroadcastReceived, is(false));
        assertThat(checkFailureBroadcastReceived, is(true));
    }

    @Test
    public void shouldProperlyHandleDownloadFailure() throws IOException, CheckException {
        final String exceptionMessage = "Test failure";

        final Update update = new Update("app1", "123", "http://aaa.bbb", "1.0", 1);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Collections.singletonList(update);
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName())).thenReturn(true);

        doThrow(new IOException(exceptionMessage))
                .doNothing()
                .when(downloader).startDownload(getUpdateContext(), update);

        update();

        verify(getScheduler()).scheduleNextCheckIfNecessary(getSettings(), false);
        verify(getMetrica(), never()).reportCheckFailure(any(), any(), any());
        verify(getMetrica()).reportDownloadFailure(update, exceptionMessage);
        verify(getErrorHandler()).onDownloadError(update, exceptionMessage, ErrorCode.UNKNOWN);
        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
    }

    @Test
    public void shouldProperlyHandleSuccess() throws IOException, CheckException {
        final Update update1 = new Update("app1", "123", "http://aaa.bbb", "1.0", 1);
        final Update update2 = new Update("app2", "456", "http://ccc.ddd", "2.0", 2);
        final List<Update> updates = Arrays.asList(update1, update2);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update1.getPackageName())).thenReturn(true);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update2.getPackageName())).thenReturn(true);

        update();

        verifyCheckSucceeded(updates);
    }

    @Test
    public void shouldSkipCheckIfNoDeviceIdAvailable() throws CheckException, IOException {
        doReturn("").when(getSystemInfoProvider()).getMetricaDeviceId();
        when(getMetrica().checkDeviceIdLocked(getUpdateContext())).thenReturn(false);

        final Update update = new Update("app1", "123", "http://aaa.bbb", "1.0", 1);
        final List<Update> updates = Collections.singletonList(update);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        update();

        verifyCheckSkipped("Device Id not available");

        doReturn(DEVICE_ID).when(getSystemInfoProvider()).getMetricaDeviceId();
    }

    @Test
    public void shouldBroadcastNoUpdatesAvailable() throws CheckException {
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        update();

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(checkSuccessNoUpdatesAvailable, is(true));
    }

    @Test
    public void shouldRejectOlderVersion() throws IOException, CheckException {
        final Update update = new Update("app", "any.package", "downloadUrl", "versionName", 1);
        final List<Update> updates = Collections.singletonList(update);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode() + 1);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        update();

        verifyNoInteractions(downloader);
        verify(getMetrica(), never()).reportCheckFailure(any(), any(), any());
        verifyNoInteractions(getErrorHandler());

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(checkSuccessBroadcastApplicableUpdates.size(), is(0));
    }

    @Test
    public void shouldAcceptOlderVersionIfApkDowngradesAllowed() throws IOException, CheckException {
        final Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setAllowApkDowngrades(true);
        configuration = configBuilder.build();
        when(configurer.fetchConfiguration()).thenReturn(configuration);
        when(ConfigurationRetriever.getConfiguration(getUpdateContext().getContext())).thenReturn(configuration);
        when(configurer.getCurrentConfiguration()).thenReturn(configuration);

        final Update update = new Update("app", "any.package", "downloadUrl", "versionName", 1);
        final List<Update> updates = Collections.singletonList(update);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode() + 1);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        update();

        verify(downloader).startDownload(getUpdateContext(), update);
        verify(getMetrica(), never()).reportCheckFailure(any(), any(), any());
        verifyNoInteractions(getErrorHandler());

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(updates, is(checkSuccessBroadcastApplicableUpdates));
    }

    @Test
    public void shouldRejectEqualVersion() throws CheckException {
        final Update update = new Update("app", "packageName", "downloadUrl", "versionName", 1);
        final List<Update> updates = Collections.singletonList(update);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode());
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        update();

        verifyNoInteractions(downloader);
        verify(getMetrica(), never()).reportCheckFailure(any(), any(), any());
        verifyNoInteractions(getErrorHandler());

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(checkSuccessBroadcastApplicableUpdates.size(), is(0));
    }

    @Test
    public void shouldRejectEqualVersionIfApkDowngradesAllowed() throws CheckException {
        final Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setAllowApkDowngrades(true);
        configuration = configBuilder.build();
        when(configurer.fetchConfiguration()).thenReturn(configuration);
        when(ConfigurationRetriever.getConfiguration(getUpdateContext().getContext())).thenReturn(configuration);
        when(configurer.getCurrentConfiguration()).thenReturn(configuration);

        final Update update = new Update("app", "packageName", "downloadUrl", "versionName", 1);
        final List<Update> updates = Collections.singletonList(update);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode());
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        update();

        verifyNoInteractions(downloader);
        verify(getMetrica(), never()).reportCheckFailure(any(), any(), any());
        verifyNoInteractions(getErrorHandler());

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(checkSuccessBroadcastApplicableUpdates.size(), is(0));
    }

    @Test
    public void shouldAcceptNewerVersion() throws IOException, CheckException {
        final Update update = new Update("app", "packageName", "downloadUrl", "versionName", 1);
        final List<Update> updates = Collections.singletonList(update);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = updates;
        when(getUpdateSource().getAppUpdates())
                .thenReturn(updatesResponse);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode() - 1);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        update();

        verify(downloader).startDownload(getUpdateContext(), update);
        verify(getMetrica(), never()).reportCheckFailure(any(), any(), any());
        verifyNoInteractions(getErrorHandler());

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(updates, is(checkSuccessBroadcastApplicableUpdates));
    }

    @Test
    public void shouldIgnoreUpdateIfAppNotInstalled() throws CheckException {
        final Update update = new Update("app", "packageName", "downloadUrl", "versionName", 1);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Collections.singletonList(update);
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(false);

        update();

        verifyNoInteractions(downloader);
        verify(getMetrica()).reportCheckSuccess(Collections.singletonList(update));
        verifyNoInteractions(getErrorHandler());
        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(checkSuccessBroadcastApplicableUpdates.isEmpty(), is(true));
    }

    @Test
    public void shouldScheduleCheckIfEnabled() {
        update();
        verify(getScheduler()).scheduleNextCheckIfNecessary(getSettings(), true);
    }

    @Test
    public void shouldScheduleRepeatedCheckIfEnabled() throws CheckException {
        when(getUpdateSource().getAppUpdates()).thenThrow(new CheckException("error"));

        update();
        verify(getScheduler()).scheduleNextCheckIfNecessary(getSettings(), false);
    }

    @Test
    public void shouldNotScheduleAnyCheckIfDisabled() {
        when(getSettings().isUserAutoCheckEnabled()).thenReturn(false);

        update();

        verify(getScheduler(), never()).scheduleUpdateCheck();
    }

    @Test
    public void shouldInstallUpdatesWithLocalPath() throws CheckException {
        final Update update1 = new Update("app1", "package1", "http://aaa.bbb", "versionName1", 1);

        final Update update2 = new Update("app2", "package2", "http://ccc.ddd", "versionName2", 2);
        update2.setLocalPath("/local/path2");

        final Update update3 = new Update("app3", "package3", "http://eee.fff", "versionName3", 3);
        update3.setLocalPath("/local/path3");

        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Arrays.asList(update1, update2, update3);

        when(getUpdateSource().getAppUpdates())
                .thenReturn(updatesResponse);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update1.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update2.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update3.getPackageName()))
                .thenReturn(true);

        update();

        verify(updateInstaller, never()).install(update1, true);
        verify(updateInstaller).install(update2, true);
        verify(updateInstaller).install(update3, true);
    }

    @Test
    public void shouldBroadcastEmptyUpdateList() {
        final Updater updater = new Updater(getUpdateContext(), getOtaUpdateContext(), getInstallContext(), downloader, updateInstaller, apkInstaller);

        shadowOf(getMainLooper()).idle();
        updater.update(true);
        shadowOf(getMainLooper()).idle();
        assertThat(checkSuccessBroadcastReceived, is(true));
    }

    @Test
    public void shouldHideAndShowUpdateAvailableNotificationIfEnabled() throws CheckException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        final Bitmap icon = Bitmap.createBitmap(10, 10, Bitmap.Config.ARGB_8888);

        when(getSettings().isAutoInstallEnabled()).thenReturn(false);
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_ALL);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode() - 1);
        when(getSystemInfoProvider().getInstalledPackageIcon(update.getPackageName()))
                .thenReturn(icon);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Collections.singletonList(update);
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        update();

        verify(getNotifier()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
        verify(getNotifier()).onUpdateAvailable(update, icon, MainActivity.class);
    }

    @Test
    public void shouldNotDisplayUpdateAvailableNotificationIfDisabled() throws CheckException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);

        when(getSettings().isAutoInstallEnabled()).thenReturn(false);
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_RESULTS_ONLY);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode() - 1);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Collections.singletonList(update);
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        update();

        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
    }

    @Test
    public void shouldNotDisplayUpdateAvailableNotificationIfAutoInstallEnabled() throws CheckException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);

        when(getSettings().isAutoInstallEnabled()).thenReturn(true);
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_ALL);

        doReturn(update.getVersionCode() - 1).when(getSystemInfoProvider()).getInstalledPackageVersionCode(update.getPackageName());
        doReturn(true).when(getSystemInfoProvider()).isPackageInstalledAndEnabled(update.getPackageName());

        UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Collections.singletonList(update);
        doReturn(updatesResponse).when(getUpdateSource()).getAppUpdates();

        update();

        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
    }

    @Test
    public void shouldDownloadPassedUpdates() throws Throwable {
        final Update update1 = new Update("app1", "package1", "http://aaa.bbb", "versionName1", 1);
        final Update update2 = new Update("app2", "package2", "http://ccc.ddd", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "http://eee.fff", "versionName3", 3);

        Updater updater = new Updater(getUpdateContext(), getOtaUpdateContext(), getInstallContext(), downloader, updateInstaller, apkInstaller);

        UpdatesContainer updates = new UpdatesContainer(Arrays.asList(update1, update2, update3));

        updater.downloadUpdates(updates);

        for (Update update : updates.updates) {
            verify(downloader, times(1)).startDownload(getUpdateContext(), update);
        }

        verifyNoInteractions(getMetrica());
        verifyNoInteractions(getErrorHandler());
    }

    @Test
    public void shouldReturnAllDownloadedUpdates() {
        Updater updater = new Updater(getUpdateContext(), getOtaUpdateContext(), getInstallContext(), downloader, updateInstaller, apkInstaller);
        updateItemsStorage.clear();

        final Update update1 = new Update("app1", "package1", "http://aaa.bbb", "versionName1", 1);
        update1.setLocalPath("uri://path");
        final Update update2 = new Update("app2", "package2", "http://ccc.ddd", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "http://eee.fff", "versionName3", 3);
        update3.setLocalPath("uri://path");
        final Update update4 = new Update("app4", "package4", "http://fff.hhh", "versionName4", 4);

        List<Update> updatesList = Arrays.asList(update1, update2, update3, update4);
        for (Update update : updatesList) {
            when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName())).thenReturn(true);
            updateItemsStorage.setItem(update);
        }

        assertThat(updater.getDownloadedUpdates().updates, containsInAnyOrder(update1, update3));
        assertThat(updater.getDownloadedUpdates().updates, not(containsInAnyOrder(update2, update4)));
    }

    @Test
    public void shouldInstallDownloadedUpdates() {
        final Update notDownloadedUpdate = new Update("app1", "package1", "http://aaa.bbb", "versionName1", 5);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(notDownloadedUpdate.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().getInstalledPackageVersionCode(notDownloadedUpdate.getPackageName()))
                .thenReturn(notDownloadedUpdate.getVersionCode() - 1);

        final Update appNotInstalledUpdated = new Update("app2", "package2", "http://ccc.ddd", "versionName2", 2);
        appNotInstalledUpdated.setLocalPath("/local/path2");
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(appNotInstalledUpdated.getPackageName()))
                .thenReturn(false);

        final Update outdatedUpdate = new Update("app3", "package3", "http://eee.fff", "versionName3", 3);
        outdatedUpdate.setLocalPath("/local/path3");
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(outdatedUpdate.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().getInstalledPackageVersionCode(outdatedUpdate.getPackageName()))
                .thenReturn(outdatedUpdate.getVersionCode());

        final Update applicableUpdate = new Update("app4", "package4", "http://hhh.ggg", "versionName4", 4);
        applicableUpdate.setLocalPath("/local/path4");
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(applicableUpdate.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().getInstalledPackageVersionCode(applicableUpdate.getPackageName()))
                .thenReturn(applicableUpdate.getVersionCode() - 1);

        updateItemsStorage.mergeUpdates(Arrays.asList(notDownloadedUpdate, appNotInstalledUpdated, outdatedUpdate, applicableUpdate));

        new Updater(getUpdateContext(), getOtaUpdateContext(), getInstallContext(), downloader, updateInstaller, apkInstaller).installDownloadedUpdates();

        verify(updateInstaller).install(applicableUpdate, false);
        verifyNoInteractions(getUpdateSource());
        verifyNoInteractions(downloader);
    }

    @Test
    public void shouldInstallDownloadedRequestedUpdates() throws CheckException {
        final Update notDownloadedUpdate = new Update("app1", "package1", "http://aaa.bbb", "versionName1", 5);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(notDownloadedUpdate.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().getInstalledPackageVersionCode(notDownloadedUpdate.getPackageName()))
                .thenReturn(notDownloadedUpdate.getVersionCode() - 1);

        final Update downloadedUpdate = new Update("app4", "package4", "http://hhh.ggg", "versionName4", 4);
        downloadedUpdate.setLocalPath("/local/path4");
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(downloadedUpdate.getPackageName()))
                .thenReturn(true);
        when(getSystemInfoProvider().getInstalledPackageVersionCode(downloadedUpdate.getPackageName()))
                .thenReturn(downloadedUpdate.getVersionCode() - 1);

        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();
        updatesResponse.updates = Arrays.asList(notDownloadedUpdate, downloadedUpdate);
        when(getUpdateSource().getAppUpdates()).thenReturn(updatesResponse);

        new Updater(getUpdateContext(), getOtaUpdateContext(), getInstallContext(), downloader, updateInstaller, apkInstaller).update(false, true);

        verify(updateInstaller, never()).install(notDownloadedUpdate, true);
        verify(updateInstaller).install(downloadedUpdate, true);

        verify(getNotifier()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
    }

    @Test
    public void shouldScheduleNextCheckSuccessIfSuccessCheck() throws CheckException {
        final Update update = new Update("app", "packageName", "downloadUrl", "versionName", 1);
        final UpdatesResponseImpl updatesResponse = new UpdatesResponseImpl();

        updatesResponse.updates = Collections.singletonList(update);

        when(getUpdateSource().getAppUpdates())
                .thenReturn(updatesResponse);

        when(getSystemInfoProvider().getInstalledPackageVersionCode(update.getPackageName()))
                .thenReturn(update.getVersionCode() - 1);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        update();

        verify(getScheduler()).scheduleNextCheckIfNecessary(getSettings(), true);
    }

    /**
     * ********** Private Methods **********
     */

    private void verifyCheckSucceeded(List<Update> updates) throws IOException {
        verify(this.updateItemsStorage, times(2)).purgeOutdatedUpdates(getSystemInfoProvider());
        verify(getDownloadDirectory()).purge(getApp(), this.updateItemsStorage.getLocalPaths());
        verify(getScheduler()).scheduleNextCheckIfNecessary(eq(getSettings()), eq(true));
        verify(getSettings()).setLastCheckTimeElapsed(anyLong());
        for (Update update : updates) {
            verify(downloader).startDownload(getUpdateContext(), update);
        }
        verify(getMetrica()).reportCheckSuccess(updates);
        verify(getErrorHandler(), never()).onCheckForUpdatesError(any());
        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);

        assertThat(checkSuccessBroadcastReceived, is(true));
        assertThat(checkSuccessNoUpdatesAvailable, is(false));
        assertThat(updates, is(checkSuccessBroadcastApplicableUpdates));

        assertThat(checkFailureBroadcastReceived, is(false));

        assertThat(checkCancelBroadcastReceived, is(false));
    }

    @SuppressWarnings("SameParameterValue")
    private void verifyCheckSkipped(String reason) throws IOException {
        verify(updateItemsStorage).purgeOutdatedUpdates(getSystemInfoProvider());
        verify(getDownloadDirectory()).purge(getApp(), updateItemsStorage.getLocalPaths());

        verify(getScheduler()).scheduleNextCheckIfNecessary(getSettings(), false);
        verify(getSettings()).setLastCheckTimeElapsed(anyLong());
        verify(getNotifier(), only()).cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
        verify(getMetrica()).reportCheckCancel(reason);

        verifyNoInteractions(downloader);
        verifyNoInteractions(getErrorHandler());

        assertThat(checkCancelBroadcastReceived, is(true));

        assertThat(checkSuccessBroadcastReceived, is(false));
        assertThat(checkSuccessNoUpdatesAvailable, is(false));
        assertThat(checkSuccessBroadcastApplicableUpdates, is(nullValue()));

        assertThat(checkFailureBroadcastReceived, is(false));
    }

    @SuppressWarnings("UnusedReturnValue") // returning actual Updater instance is useful for debug purposes
    private Updater update() {
        shadowOf(getMainLooper()).idle();
        Updater updater = new Updater(getUpdateContext(), getOtaUpdateContext(), getInstallContext(), downloader, updateInstaller, apkInstaller);
        updater.update(false);
        shadowOf(getMainLooper()).idle();
        return updater;
    }
}

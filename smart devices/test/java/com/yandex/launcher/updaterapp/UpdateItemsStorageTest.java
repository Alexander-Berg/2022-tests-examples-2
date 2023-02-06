package com.yandex.launcher.updaterapp;

import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.core.SystemInfoProvider;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.core.configure.ConfigurationRetriever;
import com.yandex.launcher.updaterapp.updatermanager.UpdateItemsStorage;

import org.junit.Before;
import org.junit.Test;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.isEmptyString;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static org.junit.Assert.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class UpdateItemsStorageTest extends BaseRobolectricTest {

    private UpdateItemsStorage updateItemsStorage;
    private Configuration configuration;

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        updateItemsStorage = new UpdateItemsStorage(getApp());
        configuration = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();
        when(ConfigurationRetriever.getConfiguration(getUpdateContext().getContext())).thenReturn(configuration);
    }

    @Test
    public void shouldMergeToEmptyUpdates() {
        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final List<Update> newUpdates = Arrays.asList(update1, update2);

        updateItemsStorage.mergeUpdates(newUpdates);

        final List<Update> resultUpdates = updateItemsStorage.getStoredUpdates();

        assertEquals(newUpdates.size(), resultUpdates.size());
        assertThat(resultUpdates, hasItem(update1));
        assertThat(resultUpdates, hasItem(update2));
    }

    @Test
    public void shouldMergeToNonEmptyUpdates() {
        final Update existingUpdate1 = new Update("app1", "package1", "/some/url/1", "versionName", 1);
        existingUpdate1.setLocalPath("/local/path1");

        updateItemsStorage.mergeUpdates(Collections.singletonList(existingUpdate1));

        final Update newUpdate1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        final Update newUpdate2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);

        updateItemsStorage.mergeUpdates(Arrays.asList(newUpdate1, newUpdate2));

        final List<Update> resultUpdates = updateItemsStorage.getStoredUpdates();

        assertEquals(2, resultUpdates.size());
        assertThat(resultUpdates, hasItem(existingUpdate1));
        assertThat(resultUpdates, hasItem(newUpdate2));
    }

    @Test
    public void shouldPurgeOutdatedUpdates() {
        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "/some/url/3", "versionName3", 3);
        updateItemsStorage.mergeUpdates(Arrays.asList(update1, update2, update3));

        final SystemInfoProvider systemInfoProvider = mock(SystemInfoProvider.class);
        when(systemInfoProvider.getInstalledPackageVersionCode(update1.getPackageName())).thenReturn(SystemInfoProvider.INVALID_APP_VERSION);
        when(systemInfoProvider.getInstalledPackageVersionCode(update2.getPackageName())).thenReturn(update2.getVersionCode() + 1);

        updateItemsStorage.purgeOutdatedUpdates(systemInfoProvider);

        final List<Update> resultUpdates = updateItemsStorage.getStoredUpdates();
        assertThat(resultUpdates, not(hasItem(update1)));
        assertThat(resultUpdates, not(hasItem(update2)));
        assertThat(resultUpdates, hasItem(update3));
    }

    @Test
    public void shouldPurgeOnlyEqualUpdatesIfApkDowngradesAllowed() {
        final Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setAllowApkDowngrades(true);
        configuration = configBuilder.build();
        when(configurer.fetchConfiguration()).thenReturn(configuration);
        when(ConfigurationRetriever.getConfiguration(getUpdateContext().getContext())).thenReturn(configuration);
        when(configurer.getCurrentConfiguration()).thenReturn(configuration);

        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "/some/url/3", "versionName3", 3);
        final Update update4 = new Update("app4", "package4", "/some/url/4", "versionName4", 4);
        updateItemsStorage.mergeUpdates(Arrays.asList(update1, update2, update3, update4));

        final SystemInfoProvider systemInfoProvider = mock(SystemInfoProvider.class);
        when(systemInfoProvider.getInstalledPackageVersionCode(update1.getPackageName())).thenReturn(SystemInfoProvider.INVALID_APP_VERSION);
        when(systemInfoProvider.getInstalledPackageVersionCode(update2.getPackageName())).thenReturn(update2.getVersionCode());
        when(systemInfoProvider.getInstalledPackageVersionCode(update3.getPackageName())).thenReturn(update3.getVersionCode() + 1);

        updateItemsStorage.purgeOutdatedUpdates(systemInfoProvider);

        final List<Update> resultUpdates = updateItemsStorage.getStoredUpdates();
        assertThat(resultUpdates, not(hasItem(update1)));
        assertThat(resultUpdates, not(hasItem(update2)));
        assertThat(resultUpdates, hasItem(update3));
        assertThat(resultUpdates, hasItem(update4));
    }

    @Test
    public void shouldReturnLocalPaths() {
        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        update1.setLocalPath("localPath1");
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "/some/url/3", "versionName3", 3);
        update3.setLocalPath("localPath3");
        updateItemsStorage.mergeUpdates(Arrays.asList(update1, update2, update3));

        assertEquals(Arrays.asList(update1.getLocalPath(), update3.getLocalPath()), updateItemsStorage.getLocalPaths());
    }

    @Test
    public void shouldReturnDownloadedUpdates() {
        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        update1.setLocalPath("localPath1");
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "/some/url/3", "versionName3", 3);
        update3.setLocalPath("localPath3");
        updateItemsStorage.mergeUpdates(Arrays.asList(update1, update2, update3));

        assertEquals(Arrays.asList(update1, update3), updateItemsStorage.getDownloadedUpdates());
    }

    @Test
    public void shouldClearUpdates() {
        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "/some/url/3", "versionName3", 3);
        updateItemsStorage.mergeUpdates(Arrays.asList(update1, update2, update3));

        assertEquals(3, updateItemsStorage.getStoredUpdates().size());

        updateItemsStorage.clear();

        assertTrue(updateItemsStorage.getStoredUpdates().isEmpty());
    }

    @Test
    public void shouldClearLocalUpdates() {
        final Update update1 = new Update("app1", "package1", "/some/url/1", "versionName1", 1);
        update1.setLocalPath("localPath1");
        final Update update2 = new Update("app2", "package2", "/some/url/2", "versionName2", 2);
        final Update update3 = new Update("app3", "package3", "/some/url/3", "versionName3", 3);
        update3.setLocalPath("localPath3");
        final Collection<Update> updates = Arrays.asList(update1, update2, update3);
        final List<String> packages = Arrays.asList(update1.getPackageName(), update2.getPackageName(), update3.getPackageName());

        updateItemsStorage.mergeUpdates(Arrays.asList(update1, update2, update3));
        updateItemsStorage.clearLocalItems();

        for (Update update : updateItemsStorage.getStoredUpdates()) {
            assertThat(update.getLocalPath(), isEmptyString());
            assertThat(packages, hasItem(update.getPackageName()));
        }
    }
}

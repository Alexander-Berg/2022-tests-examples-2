package com.yandex.launcher.core;

import static org.robolectric.Shadows.shadowOf;

import android.content.pm.PackageInfo;
import android.text.TextUtils;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.core.SystemInfoProvider;

import junit.framework.Assert;

import org.junit.Test;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.shadows.ShadowPackageManager;

public class SystemInfoProviderTest extends BaseRobolectricTest {

    @Test
    public void returnInvalidVersionForNonExistingApp() {
        final SystemInfoProvider systemInfoProvider = new SystemInfoProvider(getApp());
        Assert.assertEquals(SystemInfoProvider.INVALID_APP_VERSION,
                systemInfoProvider.getInstalledPackageVersionCode("some.incredible.package.name"));
    }

    @Test
    public void returnsValidVersionForExistingApp() {
        final ShadowPackageManager packageManager = shadowOf(RuntimeEnvironment.application.getPackageManager());
        final PackageInfo packageInfo = new PackageInfo();
        packageInfo.packageName = "package.name";
        packageInfo.versionCode = 1;
        packageManager.addPackage(packageInfo);
        final SystemInfoProvider systemInfoProvider = new SystemInfoProvider(getApp());
        Assert.assertEquals(packageInfo.versionCode, systemInfoProvider.getInstalledPackageVersionCode(packageInfo.packageName));
    }

    @Test
    public void parseDumpsysOutput() {
        Assert.assertEquals("package_1.package_2.package_3", SystemInfoProvider.parseDumsysOutput("A=package_1.package_2.package_3 "));
        Assert.assertEquals("packagename", SystemInfoProvider.parseDumsysOutput("A=packagename "));

        Assert.assertNull(SystemInfoProvider.parseDumsysOutput("com.package.name"));
        Assert.assertNull(SystemInfoProvider.parseDumsysOutput("A=com.package.name"));
        Assert.assertNull(SystemInfoProvider.parseDumsysOutput("A=package#name "));
    }

    @Test
    public void getLocale() {
        Assert.assertFalse(TextUtils.isEmpty(new SystemInfoProvider(getApp()).getLocale()));
    }

    @Test
    public void getFirmwareVersionCode() {
        final SystemInfoProvider systemInfoProvider = new SystemInfoProvider(getApp());
        systemInfoProvider.setBuildFingerprint("Realtek/RealtekATV/RealtekATV:7.1.1/NMF26Q/202:userdebug/dev-keys");
        Assert.assertEquals(systemInfoProvider.getFirmwareVersionCode(), 202);
        systemInfoProvider.setBuildFingerprint("Realtek/RealtekATV/RealtekATV:7.1.1/NMF26Q/123123123:userdebug/dev-keys");
        Assert.assertEquals(systemInfoProvider.getFirmwareVersionCode(), 123123123);
        systemInfoProvider.setBuildFingerprint("Realtek/RealtekATV/RealtekATV:7.1.1/NMF26Q:userdebug/dev-keys");
        Assert.assertEquals(systemInfoProvider.getFirmwareVersionCode(), SystemInfoProvider.INVALID_FIRMWARE_VERSION);
        systemInfoProvider.setBuildFingerprint("Realtek/RealtekATV/RealtekATV:7.1.1/NMF26Q/202:userdebug");
        Assert.assertEquals(systemInfoProvider.getFirmwareVersionCode(), SystemInfoProvider.INVALID_FIRMWARE_VERSION);
    }
}

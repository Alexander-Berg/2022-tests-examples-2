package com.yandex.launcher.updaterapp;

import android.content.ComponentName;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ActivityInfo;
import android.content.pm.ApplicationInfo;
import android.content.pm.ChangedPackages;
import android.content.pm.FeatureInfo;
import android.content.pm.IPackageInstallObserver;
import android.content.pm.InstrumentationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageInstaller;
import android.content.pm.PackageManager;
import android.content.pm.PermissionGroupInfo;
import android.content.pm.PermissionInfo;
import android.content.pm.ProviderInfo;
import android.content.pm.ResolveInfo;
import android.content.pm.ServiceInfo;
import android.content.pm.SharedLibraryInfo;
import android.content.pm.VersionedPackage;
import android.content.res.Resources;
import android.content.res.XmlResourceParser;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.RemoteException;
import android.os.UserHandle;

import java.util.List;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

public class StubPackageManager extends PackageManager {
    @Override
    public PackageInfo getPackageInfo(String packageName, int flags) {
        return null;
    }

    @Override
    public PackageInfo getPackageInfo(VersionedPackage versionedPackage, int flags) {
        return null;
    }

    @Override
    public String[] currentToCanonicalPackageNames(String[] names) {
        return new String[0];
    }

    @Override
    public String[] canonicalToCurrentPackageNames(String[] names) {
        return new String[0];
    }

    @Nullable
    @Override
    public Intent getLaunchIntentForPackage(@NonNull String packageName) {
        return null;
    }

    @Nullable
    @Override
    public Intent getLeanbackLaunchIntentForPackage(@NonNull String packageName) {
        return null;
    }

    @Override
    public int[] getPackageGids(@NonNull String packageName) {
        return new int[0];
    }

    @Override
    public int[] getPackageGids(String packageName, int flags) {
        return new int[0];
    }

    @Override
    public int getPackageUid(String packageName, int flags) {
        return 0;
    }

    @Override
    public PermissionInfo getPermissionInfo(String name, int flags) {
        return null;
    }

    @Override
    public List<PermissionInfo> queryPermissionsByGroup(String group, int flags) {
        return null;
    }

    @Override
    public PermissionGroupInfo getPermissionGroupInfo(String name, int flags) {
        return null;
    }

    @Override
    public List<PermissionGroupInfo> getAllPermissionGroups(int flags) {
        return null;
    }

    @Override
    public ApplicationInfo getApplicationInfo(String packageName, int flags) {
        return null;
    }

    @Override
    public ActivityInfo getActivityInfo(ComponentName component, int flags) {
        return null;
    }

    @Override
    public ActivityInfo getReceiverInfo(ComponentName component, int flags) {
        return null;
    }

    @Override
    public ServiceInfo getServiceInfo(ComponentName component, int flags) {
        return null;
    }

    @Override
    public ProviderInfo getProviderInfo(ComponentName component, int flags) {
        return null;
    }

    @Override
    public List<PackageInfo> getInstalledPackages(int flags) {
        return null;
    }

    @Override
    public List<PackageInfo> getPackagesHoldingPermissions(String[] permissions, int flags) {
        return null;
    }

    @Override
    public int checkPermission(String permName, String pkgName) {
        return 0;
    }

    @Override
    public boolean isPermissionRevokedByPolicy(@NonNull String permName, @NonNull String pkgName) {
        return false;
    }

    @Override
    public boolean addPermission(PermissionInfo info) {
        return false;
    }

    @Override
    public boolean addPermissionAsync(PermissionInfo info) {
        return false;
    }

    @Override
    public void removePermission(String name) {

    }

    @Override
    public int checkSignatures(String pkg1, String pkg2) {
        return 0;
    }

    @Override
    public int checkSignatures(int uid1, int uid2) {
        return 0;
    }

    @Nullable
    @Override
    public String[] getPackagesForUid(int uid) {
        return new String[0];
    }

    @Nullable
    @Override
    public String getNameForUid(int uid) {
        return null;
    }

    @Override
    public List<ApplicationInfo> getInstalledApplications(int flags) {
        return null;
    }

    @Override
    public boolean isInstantApp() {
        return false;
    }

    @Override
    public boolean isInstantApp(String packageName) {
        return false;
    }

    @Override
    public int getInstantAppCookieMaxBytes() {
        return 0;
    }

    @NonNull
    @Override
    public byte[] getInstantAppCookie() {
        return new byte[0];
    }

    @Override
    public void clearInstantAppCookie() {

    }

    @Override
    public void updateInstantAppCookie(@Nullable byte[] cookie) {

    }

    @Override
    public String[] getSystemSharedLibraryNames() {
        return new String[0];
    }

    @NonNull
    @Override
    public List<SharedLibraryInfo> getSharedLibraries(int flags) {
        return null;
    }

    @Nullable
    @Override
    public ChangedPackages getChangedPackages(int sequenceNumber) {
        return null;
    }

    @Override
    public FeatureInfo[] getSystemAvailableFeatures() {
        return new FeatureInfo[0];
    }

    @Override
    public boolean hasSystemFeature(String name) {
        return false;
    }

    @Override
    public boolean hasSystemFeature(String name, int version) {
        return false;
    }

    @Override
    public ResolveInfo resolveActivity(Intent intent, int flags) {
        return null;
    }

    @Override
    public List<ResolveInfo> queryIntentActivities(Intent intent, int flags) {
        return null;
    }

    @Override
    public List<ResolveInfo> queryIntentActivityOptions(@Nullable ComponentName caller, @Nullable Intent[] specifics, Intent intent, int flags) {
        return null;
    }

    @Override
    public List<ResolveInfo> queryBroadcastReceivers(Intent intent, int flags) {
        return null;
    }

    @Override
    public ResolveInfo resolveService(Intent intent, int flags) {
        return null;
    }

    @Override
    public List<ResolveInfo> queryIntentServices(Intent intent, int flags) {
        return null;
    }

    @Override
    public List<ResolveInfo> queryIntentContentProviders(Intent intent, int flags) {
        return null;
    }

    @Override
    public ProviderInfo resolveContentProvider(String name, int flags) {
        return null;
    }

    @Override
    public List<ProviderInfo> queryContentProviders(String processName, int uid, int flags) {
        return null;
    }

    @Override
    public InstrumentationInfo getInstrumentationInfo(ComponentName className, int flags) {
        return null;
    }

    @Override
    public List<InstrumentationInfo> queryInstrumentation(String targetPackage, int flags) {
        return null;
    }

    @Override
    public Drawable getDrawable(String packageName, int resid, ApplicationInfo appInfo) {
        return null;
    }

    @Override
    public Drawable getActivityIcon(ComponentName activityName) {
        return null;
    }

    @Override
    public Drawable getActivityIcon(Intent intent) {
        return null;
    }

    @Override
    public Drawable getActivityBanner(ComponentName activityName) {
        return null;
    }

    @Override
    public Drawable getActivityBanner(Intent intent) {
        return null;
    }

    @Override
    public Drawable getDefaultActivityIcon() {
        return null;
    }

    @Override
    public Drawable getApplicationIcon(ApplicationInfo info) {
        return null;
    }

    @Override
    public Drawable getApplicationIcon(String packageName) {
        return null;
    }

    @Override
    public Drawable getApplicationBanner(ApplicationInfo info) {
        return null;
    }

    @Override
    public Drawable getApplicationBanner(String packageName) {
        return null;
    }

    @Override
    public Drawable getActivityLogo(ComponentName activityName) {
        return null;
    }

    @Override
    public Drawable getActivityLogo(Intent intent) {
        return null;
    }

    @Override
    public Drawable getApplicationLogo(ApplicationInfo info) {
        return null;
    }

    @Override
    public Drawable getApplicationLogo(String packageName) {
        return null;
    }

    @Override
    public Drawable getUserBadgedIcon(Drawable icon, UserHandle user) {
        return null;
    }

    @Override
    public Drawable getUserBadgedDrawableForDensity(Drawable drawable, UserHandle user, Rect badgeLocation, int badgeDensity) {
        return null;
    }

    @Override
    public CharSequence getUserBadgedLabel(CharSequence label, UserHandle user) {
        return null;
    }

    @Override
    public CharSequence getText(String packageName, int resid, ApplicationInfo appInfo) {
        return null;
    }

    @Override
    public XmlResourceParser getXml(String packageName, int resid, ApplicationInfo appInfo) {
        return null;
    }

    @Override
    public CharSequence getApplicationLabel(ApplicationInfo info) {
        return null;
    }

    @Override
    public Resources getResourcesForActivity(ComponentName activityName) {
        return null;
    }

    @Override
    public Resources getResourcesForApplication(ApplicationInfo app) {
        return null;
    }

    @Override
    public Resources getResourcesForApplication(String appPackageName) {
        return null;
    }

    @Override
    public void verifyPendingInstall(int id, int verificationCode) {

    }

    @Override
    public void extendVerificationTimeout(int id, int verificationCodeAtTimeout, long millisecondsToDelay) {

    }

    @Override
    public void setInstallerPackageName(String targetPackage, String installerPackageName) {

    }

    @Override
    public String getInstallerPackageName(String packageName) {
        return null;
    }

    @Override
    public void addPackageToPreferred(String packageName) {

    }

    @Override
    public void removePackageFromPreferred(String packageName) {

    }

    @Override
    public List<PackageInfo> getPreferredPackages(int flags) {
        return null;
    }

    @Override
    public void addPreferredActivity(IntentFilter filter, int match, ComponentName[] set, ComponentName activity) {

    }

    @Override
    public void clearPackagePreferredActivities(String packageName) {

    }

    @Override
    public int getPreferredActivities(@NonNull List<IntentFilter> outFilters, @NonNull List<ComponentName> outActivities, String packageName) {
        return 0;
    }

    @Override
    public void setComponentEnabledSetting(@androidx.annotation.NonNull ComponentName componentName, int newState, int flags) {

    }

    @Override
    public int getComponentEnabledSetting(ComponentName componentName) {
        return 0;
    }

    @Override
    public void setApplicationEnabledSetting(@androidx.annotation.NonNull String packageName, int newState, int flags) {

    }

    @Override
    public int getApplicationEnabledSetting(String packageName) {
        return 0;
    }

    @Override
    public boolean isSafeMode() {
        return false;
    }

    @Override
    public void setApplicationCategoryHint(@NonNull String packageName, int categoryHint) {

    }

    @NonNull
    @Override
    public PackageInstaller getPackageInstaller() {
        return null;
    }

    @Override
    public boolean canRequestPackageInstalls() {
        return false;
    }

    public void installPackage(Uri packageURI, IPackageInstallObserver observer,
                               int flags, String installerPackageName) throws RemoteException {
    }

}

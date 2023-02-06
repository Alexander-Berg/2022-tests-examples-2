package ru.yandex.metrika.mobmet.intapi.direct;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.bundleid.AppleAppIdDao;
import ru.yandex.metrika.mobmet.bundleid.AppleAppIdMatching;
import ru.yandex.metrika.mobmet.bundleid.BundleId;
import ru.yandex.metrika.mobmet.feature.AppFeature;
import ru.yandex.metrika.mobmet.feature.AppFeatureDao;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectApp;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectAppsRequest;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectPlatform;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectPlatformBundleId;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;
import ru.yandex.metrika.mobmet.scheduler.tasks.bundleid.dao.BundleIdCachingDao;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultApp;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.randomUid;
import static ru.yandex.metrika.segments.apps.type.OperatingSystem.ANDROID;
import static ru.yandex.metrika.segments.apps.type.OperatingSystem.IOS;

public class DirectAppsTest extends AbstractMobmetIntapiTest {

    @Autowired
    private ApplicationsManageService appManageService;
    @Autowired
    private AuthUtils authUtils;
    @Autowired
    private DirectService directService;
    @Autowired
    private BundleIdCachingDao bundleIdCachingDao;
    @Autowired
    private AppleAppIdDao appleAppIdDao;
    @Autowired
    private AppFeatureDao appFeatureDao;

    private MetrikaUserDetails user;
    private MetrikaUserDetails anotherUser;


    @Before
    public void before() {
        user = authUtils.getUserByUid(randomUid());
        anotherUser = authUtils.getUserByUid(randomUid());
    }

    @Test
    public void ownerApp() {
        Application app = appManageService.createApplication(defaultApp(), user, user);

        DirectAppsRequest request = new DirectAppsRequest().withUid(user.getUid());
        List<DirectApp> actual = directService.getApplications(request);

        assertThat(actual).isEqualTo(List.of(new DirectApp(app, emptyList())));
    }

    @Test
    public void bundleIdSearch() {
        String targetBundleId = "test_bundle_id";
        String anotherBundleId = "test_bundle_id_2";

        Application app = appManageService.createApplication(defaultApp(), user, user);
        Application app2 = appManageService.createApplication(defaultApp(), user, user);
        Application anotherApp = appManageService.createApplication(defaultApp(), anotherUser, anotherUser);
        bundleIdCachingDao.addToCacheWithoutRowsCount(List.of(
                new BundleId(app.getId(), ANDROID, targetBundleId),
                new BundleId(app2.getId(), ANDROID, anotherBundleId),
                new BundleId(app2.getId(), IOS, targetBundleId),
                new BundleId(anotherApp.getId(), ANDROID, targetBundleId)
        ));
        DirectAppsRequest request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withBundleId(targetBundleId)
                .withPlatform(DirectPlatform.ANDROID);
        List<DirectApp> actual = directService.getApplications(request);
        List<DirectApp> expected = List.of(
                new DirectApp(app, List.of(new DirectPlatformBundleId(DirectPlatform.ANDROID, targetBundleId))));

        assertThat(actual).isEqualTo(expected);
    }

    @Test
    public void multipleBundleApp() {
        String androidBundleId1 = "android_bundle_id";
        String androidBundleId2 = "android_bundle_id_2";
        String iosBundleIdWithStorePage = "ios_bundle_id_with_store";
        String iosBundleIdNoStorePage = "ios_bundle_id_no_store";

        appleAppIdDao.save(List.of(new AppleAppIdMatching(42, iosBundleIdWithStorePage)));

        Application app = appManageService.createApplication(defaultApp(), user, user);
        bundleIdCachingDao.addToCacheWithoutRowsCount(List.of(
                new BundleId(app.getId(), ANDROID, androidBundleId1),
                new BundleId(app.getId(), ANDROID, androidBundleId2),
                new BundleId(app.getId(), IOS, iosBundleIdNoStorePage),
                new BundleId(app.getId(), IOS, iosBundleIdWithStorePage)
        ));
        DirectAppsRequest request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withId(app.getId());
        List<DirectApp> actual = directService.getApplications(request);
        List<DirectApp> expected = List.of(new DirectApp(app, List.of(
                new DirectPlatformBundleId(DirectPlatform.ANDROID, androidBundleId1),
                new DirectPlatformBundleId(DirectPlatform.ANDROID, androidBundleId2),
                new DirectPlatformBundleId(DirectPlatform.IOS, iosBundleIdWithStorePage))));

        assertThat(actual).isEqualTo(expected);
    }

    @Test
    public void idSearch() {
        Application app = appManageService.createApplication(defaultApp(), user, user);
        appManageService.createApplication(defaultApp(), user, user);

        DirectAppsRequest request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withId(app.getId());
        List<DirectApp> actual = directService.getApplications(request);

        assertThat(actual).isEqualTo(List.of(new DirectApp(app, emptyList())));
    }

    @Test
    public void anotherUserIdSearch() {
        appManageService.createApplication(defaultApp(), user, user);
        Application anotherApp = appManageService.createApplication(defaultApp(), anotherUser, anotherUser);

        DirectAppsRequest request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withId(anotherApp.getId());
        List<DirectApp> actual = directService.getApplications(request);

        assertThat(actual).isEmpty();
    }

    @Test
    public void testLibExclusionFilter() {
        Application app = appManageService.createApplication(defaultApp(), user, user);
        appFeatureDao.insert(singletonList(app.getId()), AppFeature.lib);

        DirectAppsRequest request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withId(app.getId());
        List<DirectApp> actual = directService.getApplications(request);

        assertThat(actual).isEmpty();
    }
}

package ru.yandex.metrika.mobmet.intapi.takeout;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.junit.BeforeClass;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import ru.yandex.metrika.api.CurrentRequestParamsHolder;
import ru.yandex.metrika.api.RequestSource;
import ru.yandex.metrika.api.gdpr.GdprDeleteDataState;
import ru.yandex.metrika.api.gdpr.GdprDeleteRequest;
import ru.yandex.metrika.api.gdpr.GdprDeleteResponse;
import ru.yandex.metrika.api.gdpr.GdprDeleteResponseData;
import ru.yandex.metrika.api.gdpr.GdprDeleteStatus;
import ru.yandex.metrika.api.gdpr.GdprError;
import ru.yandex.metrika.api.gdpr.GdprRequestDeleteResponse;
import ru.yandex.metrika.api.management.client.GrantsService;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.dao.redirect.RedirectServiceDao;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestData;
import ru.yandex.metrika.mobmet.intapi.takeout.model.gdpr.MobmetGdprCategory;
import ru.yandex.metrika.mobmet.intapi.takeout.service.TakeoutService;
import ru.yandex.metrika.mobmet.management.AppLabelService;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;
import ru.yandex.metrika.mobmet.service.TrackingPartnerService;
import ru.yandex.metrika.mobmet.service.TrackingService;
import ru.yandex.metrika.mobmet.service.TrackingUrlsService;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.api.gdpr.GdprDeleteDataState.delete_in_progress;
import static ru.yandex.metrika.api.gdpr.GdprDeleteDataState.empty;
import static ru.yandex.metrika.api.gdpr.GdprDeleteDataState.ready_to_delete;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultApp;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultCampaign;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultLabel;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultPartner;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultTargetUrl;
import static ru.yandex.metrika.mobmet.intapi.common.TestTvmServices.PASSPORT_FRONTEND;
import static ru.yandex.metrika.mobmet.intapi.takeout.model.gdpr.MobmetGdprCategory.APPLICATIONS;
import static ru.yandex.metrika.mobmet.intapi.takeout.model.gdpr.MobmetGdprCategory.LABELS;
import static ru.yandex.metrika.mobmet.intapi.takeout.model.gdpr.MobmetGdprCategory.MEDIA_SOURCES;

public class TakeoutDeleteControllerTest extends AbstractMobmetIntapiTest {

    @Autowired
    private AuthUtils authUtils;
    @Autowired
    private ApplicationsManageService appManageService;
    @Autowired
    private TrackingPartnerService partnerService;
    @Autowired
    private AppLabelService labelService;
    @Autowired
    private TakeoutService takeoutService;

    @Autowired
    private RedirectServiceDao redirectServiceDao;
    @Autowired
    private TrackingService trackingService;
    @Autowired
    private TrackingUrlsService trackingUrlsService;
    @Autowired
    private GrantsService grantsService;

    @BeforeClass
    public static void setupClass() {
        // нужно чтобы создать трекер. Выносим в BeforeClass потому что статика
        CurrentRequestParamsHolder.setRequestSource(RequestSource.INTERFACE);
    }

    @Test
    public void testNoData() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        performStatusAndExpectResponse(user, makeResponse(empty, empty, empty));
    }

    @Test
    public void testWithApp() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        appManageService.createApplication(defaultApp(), user, user);
        performStatusAndExpectResponse(user, makeResponse(ready_to_delete, empty, empty));
        assertThat(takeoutState(user).getApplications()).isNotEmpty();
    }

    @Test
    public void testWithPartner() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        partnerService.createPartner(defaultPartner(user.getUid()));
        performStatusAndExpectResponse(user, makeResponse(empty, ready_to_delete, empty));
        assertThat(takeoutState(user).getMediaSources()).isNotEmpty();
    }

    @Test
    public void testWithLabel() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        labelService.createLabel(defaultLabel(user.getUid()), user);
        performStatusAndExpectResponse(user, makeResponse(empty, empty, ready_to_delete));
        assertThat(takeoutState(user).getLabels()).isNotEmpty();
    }

    @Test
    public void testWithAll() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user);
        performStatusAndExpectResponse(user, makeResponse(ready_to_delete, ready_to_delete, ready_to_delete));
        TakeoutOkResponse takeoutState = takeoutState(user);
        assertThat(takeoutState.getApplications()).isNotEmpty();
        assertThat(takeoutState.getMediaSources()).isNotEmpty();
        assertThat(takeoutState.getLabels()).isNotEmpty();
    }

    @Test
    public void testAppDelete() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user);
        performDelete(user, List.of(APPLICATIONS));
        performStatusAndExpectResponse(user, makeResponse(delete_in_progress, ready_to_delete, ready_to_delete));
        assertThat(takeoutState(user).getApplications()).isEmpty();
    }

    @Test
    public void testPartnerDelete() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user);
        performDelete(user, List.of(MEDIA_SOURCES));
        performStatusAndExpectResponse(user, makeResponse(ready_to_delete, delete_in_progress, ready_to_delete));
        assertThat(takeoutState(user).getMediaSources()).isEmpty();
    }

    @Test
    public void testLabelsDelete() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user);
        performDelete(user, List.of(LABELS));
        performStatusAndExpectResponse(user, makeResponse(ready_to_delete, ready_to_delete, delete_in_progress));
        assertThat(takeoutState(user).getLabels()).isEmpty();
    }

    @Test
    public void testAllDelete() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user);
        performDelete(user, List.of(APPLICATIONS, MEDIA_SOURCES, LABELS));
        performStatusAndExpectResponse(user, makeResponse(delete_in_progress, delete_in_progress, delete_in_progress));
        assertThat(takeoutState(user).getApplications()).isNotEmpty();
        assertThat(takeoutState(user).getMediaSources()).isNotEmpty();
        assertThat(takeoutState(user).getLabels()).isNotEmpty();
    }

    @Test
    public void testDeleteIndependence() throws Exception {
        var user1 = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user1);
        var user2 = authUtils.getUserByUid(TestData.randomUid());
        createAllTopEntry(user2);

        performDelete(user1, List.of(APPLICATIONS, MEDIA_SOURCES, LABELS));
        performStatusAndExpectResponse(user1, makeResponse(delete_in_progress, delete_in_progress, delete_in_progress));
        performStatusAndExpectResponse(user2, makeResponse(ready_to_delete, ready_to_delete, ready_to_delete));
    }

    @Test
    public void testNotDeletablePartner() throws Exception {
        var partnerOwner = authUtils.getUserByUid(TestData.randomUid());
        var partner = partnerService.createPartner(defaultPartner(partnerOwner.getUid()));
        appManageService.createApplication(defaultApp(), partnerOwner, partnerOwner);
        labelService.createLabel(defaultLabel(partnerOwner.getUid()), partnerOwner);

        var partnerUser = authUtils.getUserByUid(TestData.randomUid());
        var partnerUserApp = appManageService.createApplication(defaultApp(), partnerUser, partnerUser);
        var partnerUserTrackingUrl = trackingUrlsService.create(partnerUserApp.getId(), defaultTargetUrl());
        grantsService.saveGrant(partnerUser.getUid(), partnerUserApp.getId(),
                GrantType.view, partnerOwner.getUid(), "", new Date());
        var trackingId = redirectServiceDao.nextTrackingId();
        var campaign = defaultCampaign(trackingId, partnerUserApp.getId(),
                partner.getId(), partnerUserTrackingUrl.getId());
        trackingService.createCampaign(campaign, false, partnerUser, partnerUser);

        var expectedError = new GdprError("not_deletable_media_sources",
                "Some media sources can't be deleted because have active trackers. " +
                        "Media sources ids: " + partner.getId());
        performDeleteAndExpectError(partnerOwner, List.of(APPLICATIONS, MEDIA_SOURCES, LABELS), expectedError);
        performStatusAndExpectResponse(partnerOwner, makeResponse(ready_to_delete, ready_to_delete, ready_to_delete));
    }

    private void createAllTopEntry(MetrikaUserDetails user) {
        appManageService.createApplication(defaultApp(), user, user);
        partnerService.createPartner(defaultPartner(user.getUid()));
        labelService.createLabel(defaultLabel(user.getUid()), user);
    }

    private void performStatusAndExpectResponse(MetrikaUserDetails user, String expectedResponse) throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/1/takeout/status")
                        .headers(PASSPORT_FRONTEND.getUserHeaders(user.getUid())))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json(expectedResponse));
    }

    private void performDelete(MetrikaUserDetails user, List<MobmetGdprCategory> categories) throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.post("/1/takeout/delete")
                        .headers(PASSPORT_FRONTEND.getUserHeaders(user.getUid()))
                        .content(writeAsString(new GdprDeleteRequest(F.map(categories, MobmetGdprCategory::getId)))))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json(writeAsString(GdprDeleteResponse.successResponse())));
    }

    private void performDeleteAndExpectError(MetrikaUserDetails user,
                                             List<MobmetGdprCategory> categories,
                                             GdprError error) throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.post("/1/takeout/delete")
                        .headers(PASSPORT_FRONTEND.getUserHeaders(user.getUid()))
                        .content(writeAsString(new GdprDeleteRequest(F.map(categories, MobmetGdprCategory::getId)))))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json(writeAsString(GdprDeleteResponse.error(error))));
    }

    private String makeResponse(GdprDeleteDataState appState,
                                GdprDeleteDataState partnersState,
                                GdprDeleteDataState labelsState) throws Exception {
        List<GdprDeleteResponseData> categories = new ArrayList<>();

        categories.add(new GdprDeleteResponseData(
                appState,
                null,
                APPLICATIONS.getName(),
                APPLICATIONS.getId()));

        categories.add(new GdprDeleteResponseData(
                partnersState,
                null,
                MEDIA_SOURCES.getName(),
                MEDIA_SOURCES.getId()));

        categories.add(new GdprDeleteResponseData(
                labelsState,
                null,
                LABELS.getName(),
                LABELS.getId()));

        GdprRequestDeleteResponse response = new GdprRequestDeleteResponse(GdprDeleteStatus.ok, categories);
        return writeAsString(response);
    }

    private String writeAsString(Object obj) throws JsonProcessingException {
        return ObjectMappersFactory.getDefaultMapper().writeValueAsString(obj);
    }

    private TakeoutOkResponse takeoutState(MetrikaUserDetails mud) {
        TakeoutResponse response = takeoutService.takeout(mud.getUid());
        return TakeoutTestUtils.readOkTakeoutResponse(response);
    }
}

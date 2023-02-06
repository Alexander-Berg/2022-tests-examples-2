package ru.yandex.metrika.mobmet.report;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.push.common.campaigns.dao.PushApiCampaignsDao;
import ru.yandex.metrika.mobmet.push.common.campaigns.dao.PushCampaignsDao;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBrief;
import ru.yandex.metrika.mobmet.push.service.PushCampaignMetaService;
import ru.yandex.metrika.mobmet.report.generator.SegmentGenerator;
import ru.yandex.metrika.mobmet.report.model.frontend.FrontendParams;
import ru.yandex.metrika.mobmet.report.model.frontend.MobmetFrontendParamsParser;
import ru.yandex.metrika.mobmet.report.model.frontend.item.ItemFilter;
import ru.yandex.metrika.mobmet.report.model.frontend.item.TreeFilterValue;
import ru.yandex.metrika.mobmet.report.model.frontend.item.TreePath;
import ru.yandex.metrika.mobmet.service.SegmentConversionService;
import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.json.JsonUtils;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@RunWith(Parameterized.class)
public class PushSegmentConversionTest {

    @Parameterized.Parameter
    public FrontendParams params;
    @Parameterized.Parameter(1)
    public String expected;

    private SegmentConversionService service;

    @Parameterized.Parameters(name = "Params: {0}, report type: {1}")
    public static Collection<Object[]> init() {
        return ImmutableList.<Object[]>builder()
                .add(params(
                        segment("pushOpened_v2", false, List.of(List.of("campaign.36"))),
                        "exists ym:pc:device with (actionType=='open' and (campaignInfo=='campaign.36') and specialDefaultDate>='2021-09-18' and specialDefaultDate<='today')"))
                .add(params(
                        segment("pushOpened_v2", false, List.of(List.of("group.16"))),
                        "exists ym:pc:device with (actionType=='open' and (campaignInfo=='group.16') and specialDefaultDate>='2021-09-04' and specialDefaultDate<='today')"))
                .add(params(
                        segment("pushOpened_v2", false, List.of(List.of("group.1611"))),
                        "exists ym:pc:device with (actionType=='open' and (campaignInfo=='group.1611') and specialDefaultDate>='2015-01-01' and specialDefaultDate<='today')"))
                .add(params(
                        segment("pushReceived_v2", false, List.of(List.of("campaign.36"), List.of("group.16"))),
                        "exists ym:pc:device with (actionType=='receive' and ((campaignInfo=='campaign.36') or (campaignInfo=='group.16')) and specialDefaultDate>='2021-09-04' and specialDefaultDate<='today')"))
                .add(params(
                        segment("pushReceived_v2", false, List.of(List.of("campaign.36"), List.of("group.16"), List.of("group.1611"))),
                        "exists ym:pc:device with (actionType=='receive' and ((campaignInfo=='campaign.36') or (campaignInfo=='group.16') or (campaignInfo=='group.1611')) and specialDefaultDate>='2015-01-01' and specialDefaultDate<='today')"))
                .add(params(
                        segment("pushSkipped_v2", true, List.of(List.of("group.16"))),
                        "not exists ym:pc:device with (actionType=='dismiss' and (campaignInfo=='group.16') and specialDefaultDate>='2021-09-04' and specialDefaultDate<='today')"))
                .build();
    }

    private static Object[] params(FrontendParams segment, String expected) {
        return new Object[]{segment, expected};
    }

    private static FrontendParams segment(String key, boolean inverted, List<List<String>> paths) {
        return new FrontendParams(List.of(
                new ItemFilter<>(key, new TreeFilterValue(inverted, F.map(paths, TreePath::new)))));
    }

    @Before
    public void before() {
        MobmetFrontendParamsParser parsedSegment = new MobmetFrontendParamsParser();

        PushCampaignsDao campaignsDao = mock(PushCampaignsDao.class);
        PushApiCampaignsDao apiCampaignsDao = mock(PushApiCampaignsDao.class);

        when(campaignsDao.loadCampaignsList(Set.of(36L))).thenReturn(List.of(brief(36, "2021-09-28")));
        when(apiCampaignsDao.loadPushApiCampaignsList(Set.of(16L))).thenReturn(List.of(brief(16, "2021-09-14")));
        when(apiCampaignsDao.loadPushApiCampaignsList(Set.of(16L, 1611L))).thenReturn(List.of(brief(16, "2021-09-14")));

        PushCampaignMetaService pushService = new PushCampaignMetaService(campaignsDao, apiCampaignsDao);
        pushService.init();

        Map<ReportType, SegmentGenerator> generators = new SegmentGeneratorsFactory(pushService).build();
        service = new SegmentConversionService(parsedSegment, generators, mock(ApiInputValidator.class));
    }

    private static PushCampaignBrief brief(int id, String date) {
        LocalDate localDate = LocalDate.parse(date);
        LocalDateTime localDateTime = localDate.atStartOfDay();
        Instant instant = localDateTime.toInstant(ZoneOffset.UTC);
        PushCampaignBrief brief = new PushCampaignBrief();
        brief.setId(id);
        brief.setCreationTime(new Date(instant.toEpochMilli()));
        return brief;
    }

    @Test
    public void convertForReport() {
        String json = JsonUtils.uncheckedAsString(ObjectMappersFactory.getDefaultMapper(), params);
        String actual = service.convertForReport(ReportType.AUDIENCE, json);
        assertEquals(expected, actual);
    }
}

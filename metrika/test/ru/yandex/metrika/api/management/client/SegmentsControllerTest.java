package ru.yandex.metrika.api.management.client;

import java.util.ArrayList;
import java.util.List;

import com.google.common.collect.Lists;
import org.apache.log4j.BasicConfigurator;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.InjectMocks;
import org.mockito.Matchers;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.Spy;
import org.mockito.runners.MockitoJUnitRunner;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.util.NestedServletException;

import ru.yandex.metrika.api.ObjectNotFoundException;
import ru.yandex.metrika.api.error.LimitException;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentParseService;
import ru.yandex.metrika.api.management.client.segments.SegmentRetargeting;
import ru.yandex.metrika.api.management.client.segments.SegmentsDao;
import ru.yandex.metrika.api.management.client.segments.SegmentsExpressionHistoryDao;
import ru.yandex.metrika.api.management.client.segments.SegmentsService;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.spring.auth.TargetUserHandlerMethodArgumentResolver;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.core.Is.is;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.fail;
import static org.mockito.ArgumentMatchers.anyObject;
import static org.mockito.Matchers.anyInt;
import static org.mockito.Matchers.anyListOf;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.anyVararg;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.isA;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.api.management.client.segments.SegmentRetargeting.ALLOW;
import static ru.yandex.metrika.api.management.client.segments.SegmentSource.API;
import static ru.yandex.metrika.api.management.client.segments.SegmentSource.INTERFACE;
import static ru.yandex.metrika.api.management.client.segments.SegmentStatus.active;
import static ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass.NOT_STREAMABLE;

/**
 * The Unit test for {@link SegmentsController}
 */
@RunWith(MockitoJUnitRunner.class)
public class SegmentsControllerTest {

    @Mock
    private SegmentsDao segmentsDao;
    @Mock
    private MySqlJdbcTemplate retargetingDb;
    @Mock
    private MySqlJdbcTemplate convMain;
    @Mock
    private CounterLimitsService limitsService;
    @Mock
    private SegmentParseService segmentParseService;
    @Mock
    private SegmentsExpressionHistoryDao segmentsExpressionHistoryDao;
    @Mock
    private MetrikaUserDetails metrikaUserDetails;

    @Spy
    @InjectMocks
    private SegmentsService segmentsService = Mockito.spy(new SegmentsService());

    @InjectMocks
    private SegmentsController segmentsController;

    @InjectMocks
    private TrueSegmentsController trueSegmentsController;

    @InjectMocks
    private TargetUserHandlerMethodArgumentResolver userArgResolver;

    @Captor
    private ArgumentCaptor<Object> varArgCaptor;

    @Captor
    private ArgumentCaptor<Segment> segmentArgumentCaptor;

    @BeforeClass
    public static void setUp() {
        BasicConfigurator.configure();
    }

    @Before
    public void before() {
        AuthUtils.setUserDetails(metrikaUserDetails);
    }

    @After
    public void after() {
        SecurityContextHolder.clearContext();
    }

    @Test
    public void testGetByCounter() throws Exception {
        when(convMain.query(anyString(), Matchers.<RowMapper<Segment>>any(), anyVararg())).thenReturn(
                Lists.newArrayList(
                        new Segment(1, 2, "3", "some_expression", 1, 100500, true, active, INTERFACE, SegmentRetargeting.NOT_ALLOW, NOT_STREAMABLE),
                        new Segment(2, 2, "3", "some_expression1", 1, 100500, true, active, INTERFACE, SegmentRetargeting.NOT_ALLOW, NOT_STREAMABLE),
                        new Segment(3, 2, "3", "some_expression2", 1, 100500, true, active, API, SegmentRetargeting.NOT_ALLOW, NOT_STREAMABLE)
                )
        );
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController).build();
        MvcResult result = mockMvc.perform(get("/management/v1/counter/32/apisegment/segments")
                .accept(MediaType.parseMediaType("application/json;charset=UTF-8")))
                .andReturn();

        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json;charset=UTF-8"));
//                .andExpect(jsonPath("$.segments[*].segmentId", hasItems(1, 2, 3)))
//                .andExpect(jsonPath("$.segments[*].segmentSource", hasItems("interface", "api")))
    }

    @Test
    public void testGetById() throws Exception {
        when(segmentsDao.getSegments(anyListOf(Integer.class), anyInt())).thenReturn(
                Lists.newArrayList(
                        new Segment(42, 2, "3", "some_expression", 1, 100500, true, active, API, SegmentRetargeting.NOT_ALLOW, NOT_STREAMABLE)
                )
        );
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController).build();
        MvcResult result = mockMvc.perform(get("/management/v1/counter/32/apisegment/segment/42")
                .accept(MediaType.parseMediaType("application/json;charset=UTF-8")))
                .andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json;charset=UTF-8"))
                .andExpect(jsonPath("$.segment.segmentId", is(42))).andReturn();

        System.out.println(result.getResponse().getContentAsString());
    }

    @Test
    public void testGetById_404() throws Exception {
        when(segmentsDao.getSegments(anyListOf(Integer.class), anyInt())).thenReturn(
                new ArrayList<>()
        );
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController).build();
        try {
            MvcResult result = mockMvc.perform(get("/management/v1/counter/32/apisegment/segment/42"))
                    .andReturn();
            mockMvc.perform(asyncDispatch(result))
                    .andExpect(status().isNotFound());
        } catch (NestedServletException e) {
            assertThat(e.getCause(), instanceOf(ObjectNotFoundException.class));
            return;
        }
        fail();
    }

    @Test
    public void testCreateSegment() throws Exception {
        when(limitsService.getCounterLimits(anyInt())).thenReturn(new CounterLimits());
        // count and exists
        doReturn(1)
                .doReturn(0)
                .when(convMain).queryForObject(anyString(), Matchers.<Class<?>>any(), anyVararg());

        // return object when it's created
        when(segmentsDao.getSegments(anyListOf(Integer.class), anyInt())).thenReturn(
                Lists.newArrayList(new Segment()));

        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController)
                .setCustomArgumentResolvers(userArgResolver)
                .build();

        MvcResult result = mockMvc.perform(post("/management/v1/counter/32/apisegment/segments")
                .accept(MediaType.parseMediaType("application/json;charset=UTF-8"))
                .header("Content-Type", "application/json;charset=UTF-8")
                .content("{\"segment\":{\"segmentId\":42,\"counterId\":2,\"name\":\"3\",\"expression\":\"some_expression\",\"isRetargeting\":1,\"segmentSource\":\"interface\"},\"_profile\":null}\n"))
                .andReturn();

        mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());

        ArgumentCaptor<Segment> segmentCaptor = ArgumentCaptor.forClass(Segment.class);
        verify(segmentsDao).createSegment(anyObject(), segmentCaptor.capture(), eq(32));
        assertThat(segmentCaptor.getValue().getSegmentSource(), is(API));
    }

    @Test
    public void testCreateSegment_ApiLimitExceeded() throws Exception {
        doReturn(42). // total segments
                doReturn(0). // other segments with same name
                when(convMain).queryForObject(anyString(), Matchers.<Class<?>>any(), anyVararg());
        final int counterId = 32;

        doReturn(new CounterLimits(0, 0, 0, 0, 0, new CounterSegmentLimits(0, 42)))
                .when(limitsService).getCounterLimits(eq(counterId));

        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController)
                .setCustomArgumentResolvers(userArgResolver)
                .build();

        try {
            MvcResult result = mockMvc.perform(post("/management/v1/counter/" + counterId + "/apisegment/segments")
                    .accept(MediaType.parseMediaType("application/json;charset=UTF-8"))
                    .header("Content-Type", "application/json;charset=UTF-8")
                    .content("{\"segment\":{\"segmentId\":42,\"counterId\":" + counterId + ",\"name\":\"3\",\"expression\":\"some_expression\",\"isRetargeting\":1,\"segmentSource\":\"api\"},\"_profile\":null}\n"))
                    .andReturn();
            mockMvc.perform(asyncDispatch(result))
                    .andExpect(status().isOk());
        } catch (NestedServletException e) {
            assertThat(e.getCause(), instanceOf(LimitException.class));
        }
    }

    @Test
    public void testForbiddenToUpdate() throws Exception {
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(trueSegmentsController)
                .setCustomArgumentResolvers(userArgResolver)
                .build();
        try {
            MvcResult result = mockMvc.perform(put("/management/v1/counter/32/segment/10")
                    .accept(MediaType.parseMediaType("application/json;charset=UTF-8"))
                    .header("Content-Type", "application/json;charset=UTF-8")
                    .content("{\"segment\":{\"segmentId\":42,\"counterId\":2,\"name\":\"3\",\"expression\":\"some_expression\",\"isRetargeting\":1,\"segmentSource\":\"api\"},\"_profile\":null}\n"))
                    .andReturn();
            mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
        } catch (NestedServletException e) {
            assertThat(e.getCause(), instanceOf(ObjectNotFoundException.class));
            return;
        }
        fail();
    }

    @Test
    public void testUpdate_ForbiddenToUpdate() throws Exception {
        doReturn(42). // total segments
                doReturn(0). // other segments with same name
                when(convMain).queryForObject(anyString(), Matchers.<Class<?>>any(), anyVararg());

        final int counterId = 32;

        // update checks for existence of segment with same id
        when(segmentsDao.getSegments(eq(Lists.newArrayList(42)), eq(counterId))).thenReturn(
                Lists.newArrayList(new Segment()));

        doReturn(new CounterLimits(0, 0, 0, 0, 0, new CounterSegmentLimits(0, 42)))
                .when(limitsService).getCounterLimits(eq(counterId));

        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController)
                .setCustomArgumentResolvers(userArgResolver)
                .build();

        try {
            MvcResult result = mockMvc.perform(put("/management/v1/counter/" + counterId + "/apisegment/segment/42")
                    .accept(MediaType.parseMediaType("application/json;charset=UTF-8"))
                    .header("Content-Type", "application/json;charset=UTF-8")
                    .content("{\"segment\":{\"segmentId\":42,\"counterId\":" + counterId + ",\"name\":\"3\",\"expression\":\"some_expression\",\"isRetargeting\":1,\"segmentSource\":\"interface\"},\"_profile\":null}\n"))
                    .andReturn();
            mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
        } catch (NestedServletException e) {
            assertThat(e.getCause(), instanceOf(LimitException.class));
        }

        verify(convMain, times(1)).queryForObject(
                eq("SELECT COUNT(*) FROM segments WHERE `counter_id` = ? AND `status` = ? AND `segment_source` = ?"),
                Matchers.<Class<?>>any(),
                varArgCaptor.capture());

        List<Object> allValues = varArgCaptor.getAllValues();
        assertThat(allValues, hasItems(32, "active", "api")); // check that we are requesting count for API
    }

    @Test
    public void testUpdate_AllowedToUpdate() throws Exception {
        final int counterId = 32;
        // select for update
        when(segmentsDao.getSegments(eq(Lists.newArrayList(42)), eq(counterId))).thenReturn(
                Lists.newArrayList(new Segment(
                        42, counterId, "", "old_expression", 1, 0, false,
                        active, API, ALLOW, NOT_STREAMABLE
                )));

        // stub for check limits
        when(convMain.queryForObject(
                eq("SELECT COUNT(*) FROM segments WHERE `counter_id` = ? AND `status` = ? AND `segment_source` = ?"),
                Matchers.<Class<Integer>>any(), anyVararg())).thenReturn(1);

        // stub to check for other segments with same name
        when(convMain.queryForObject(
                eq("SELECT COUNT(*) FROM segments WHERE counter_id = ? AND segment_id <> ? AND `name` = ? AND `status` = ?"),
                Matchers.<Class<Integer>>any(), anyVararg())).thenReturn(0);

        // stub for update
        when(segmentsDao.updateSegment(anyInt(), anyInt(), isA(Segment.class))).thenReturn(1);

        // stub to test something with retargeting
        when(convMain.queryForObject(
                eq("SELECT direct_retargeting OR display_retargeting OR adfox_retargeting OR banana_retargeting FROM segments WHERE segment_id = ?"),
                Matchers.<Class<Boolean>>any(), anyVararg())).thenReturn(false);

        doReturn(new CounterLimits(0, 0, 0, 0, 0, new CounterSegmentLimits(0, 42)))
                .when(limitsService).getCounterLimits(eq(counterId));

        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController)
                .setCustomArgumentResolvers(userArgResolver)
                .build();

        MvcResult result = mockMvc.perform(put("/management/v1/counter/" + counterId + "/apisegment/segment/42")
                .accept(MediaType.parseMediaType("application/json;charset=UTF-8"))
                .header("Content-Type", "application/json;charset=UTF-8")
                .content("{\"segment\":{\"segmentId\":42,\"counterId\":" + counterId + ",\"name\":\"new_name\",\"expression\":\"new_expression\",\"isRetargeting\":1,\"segmentSource\":\"interface\"},\"_profile\":null}\n"))
                .andReturn();
        mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());

        verify(segmentsDao, times(1)).updateSegment(
                eq(42),
                eq(32),
                segmentArgumentCaptor.capture()
        );

        verify(segmentsExpressionHistoryDao, times(1)).saveVersion(
                eq(42), eq(1), eq("old_expression")
        );

        Segment segment = segmentArgumentCaptor.getValue();
        assertThat(segment.getSegmentSource(), is(API));
        assertThat(segment.getName(), is("new_name"));
        assertThat(segment.getExpression(), is("new_expression"));
    }

    @Test
    public void testForbiddenToDelete() throws Exception {
        when(segmentsDao.getSegments(anyListOf(Integer.class), anyInt())).thenReturn(
                Lists.newArrayList(
                        new Segment()
                )
        );

        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentsController)
                .build();
        try {
            MvcResult result = mockMvc.perform(delete("/management/v1/counter/32/apisegment/segment/10"))
                    .andReturn();
            mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
        } catch (NestedServletException e) {
            assertThat(e.getCause(), instanceOf(AccessDeniedException.class));
            return;
        }
        fail();
    }

}

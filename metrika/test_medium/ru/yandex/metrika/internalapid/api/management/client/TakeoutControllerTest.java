package ru.yandex.metrika.internalapid.api.management.client;

import java.util.List;
import java.util.Random;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import ru.yandex.metrika.api.gdpr.GdprDeleteRequest;
import ru.yandex.metrika.api.gdpr.GdprDeleteResponse;
import ru.yandex.metrika.api.gdpr.GdprRequestDeleteResponse;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.internalapid.api.config.TakeoutControllerConfiguration;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;

import static org.hamcrest.Matchers.containsString;
import static org.mockito.ArgumentMatchers.any;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.request;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(SpringJUnit4ClassRunner.class)
@WebAppConfiguration
@ContextConfiguration(classes = {TakeoutControllerConfiguration.class})
public class TakeoutControllerTest extends BaseIntapiTest {

    private static final String URI_STATUS = "/1/takeout/status";
    private static final String URI_DELETE = "/1/takeout/delete";
    private static final String URI_UNDELETE = "/admin/gdpr_undelete";

    private static final long NO_DATA_USER_UID = 41;
    private static final long WITH_DATA_USER_UID = 42;
    private static final long TRY_TO_DELETE_DATA_USER_UID = 43;

    private static final long TRY_TO_UNDELETE_DATA_USER_UID = 44;
    private int uniqCounterId = (new Random()).nextInt(1000);

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void setup() {
        mockMvcBaseSetup();
    }

    @Test
    public void testNoData() throws Exception {
        getUserByUid(NO_DATA_USER_UID);
        var mvcResult = mockMvc.perform(MockMvcRequestBuilders.get(URI_STATUS))
                .andExpect(status().isOk())
                .andReturn();

        mockMvc.perform(asyncDispatch(mvcResult))
                .andExpect(status().isOk())
                .andExpect(MockMvcResultMatchers.content().json(
                        getObjectMapper().writeValueAsString(GdprRequestDeleteResponse.nodata(null)))
                )
                .andReturn();
    }

    @Test
    public void testWithData() throws Exception {
        getUserByUid(WITH_DATA_USER_UID);
        createCounter(uniqCounterId, WITH_DATA_USER_UID);
        ++uniqCounterId;

        var mvcResult = mockMvc.perform(MockMvcRequestBuilders.get(URI_STATUS))
                .andDo(print())
                .andExpect(status().isOk())
                .andReturn();

        mockMvc.perform(asyncDispatch(mvcResult))
                .andExpect(status().isOk())
                .andExpect(MockMvcResultMatchers.content().json(
                        getObjectMapper().writeValueAsString(GdprRequestDeleteResponse.createResponse(false, null)))
                )
                .andReturn();
    }

    @Test
    public void testDelete() throws Exception {
        getUserByUid(TRY_TO_DELETE_DATA_USER_UID);
        createCounter(uniqCounterId, TRY_TO_DELETE_DATA_USER_UID);
        ++uniqCounterId;

        var mvcResultDelete = mockMvc.perform(MockMvcRequestBuilders.post(URI_DELETE)
                        .content(getObjectMapper().writeValueAsString(new GdprDeleteRequest(List.of(1)))))
                .andDo(print())
                .andExpect(status().isOk())
                .andReturn();

        mockMvc.perform(asyncDispatch(mvcResultDelete))
                .andExpect(status().isOk())
                .andExpect(MockMvcResultMatchers.content().json(
                        getObjectMapper().writeValueAsString(GdprDeleteResponse.successResponse()))
                )
                .andReturn();

        getUserByUid(TRY_TO_DELETE_DATA_USER_UID);
        var mvcResult = mockMvc.perform(MockMvcRequestBuilders.get(URI_STATUS))
                .andExpect(request().asyncStarted())
                .andReturn();
        mockMvc.perform(asyncDispatch(mvcResult))
                .andExpect(status().isOk())
                .andExpect(MockMvcResultMatchers.content().json(
                        getObjectMapper().writeValueAsString(GdprRequestDeleteResponse.createResponse(true, any())),
                        false)
                )
                .andReturn();
    }

    @Test
    public void testUndelete() throws Exception {
        getManagerUserByUid(TRY_TO_UNDELETE_DATA_USER_UID);
        createCounter(uniqCounterId, TRY_TO_UNDELETE_DATA_USER_UID);
        var createdCounterId = uniqCounterId;
        ++uniqCounterId;

        var mvcResultDelete = mockMvc.perform(MockMvcRequestBuilders.post(URI_DELETE)
                        .content(getObjectMapper().writeValueAsString(new GdprDeleteRequest(List.of(1)))))
                .andDo(print())
                .andExpect(status().isOk())
                .andReturn();

        mockMvc.perform(asyncDispatch(mvcResultDelete))
                .andExpect(status().isOk())
                .andExpect(MockMvcResultMatchers.content().json(
                        getObjectMapper().writeValueAsString(GdprDeleteResponse.successResponse()))
                )
                .andReturn();

        var mvcResultUndelete = mockMvc.perform(MockMvcRequestBuilders.post(URI_UNDELETE + "?counter_id=" + createdCounterId))
                .andDo(print())
                .andExpect(status().isOk())
                .andReturn();
        mockMvc.perform(asyncDispatch(mvcResultUndelete))
                .andExpect(MockMvcResultMatchers.content().string(containsString("Ok. Counter " + createdCounterId + " successfully gdpr undeleted.")))
                .andReturn();
    }

    @Test
    public void testUndeleteNoCounter() throws Exception {
        getManagerUserByUid(TRY_TO_UNDELETE_DATA_USER_UID);
        var notExistedCounterId = new Random().nextInt(1000) + 1000;

        var mvcResultUndelete = mockMvc.perform(MockMvcRequestBuilders.post(URI_UNDELETE + "?counter_id=" + notExistedCounterId))
                .andDo(print())
                .andExpect(status().isOk())
                .andReturn();

        mockMvc.perform(asyncDispatch(mvcResultUndelete))
                .andExpect(MockMvcResultMatchers.content().string(containsString("Error. Found 0 counters possible to undelete instead of 1. counter_id: " + notExistedCounterId)))
                .andReturn();
    }

    protected ObjectMapper getObjectMapper() {
        return wac.getBean(MetrikaApiMessageConverter.class).getObjectMapper();
    }
}

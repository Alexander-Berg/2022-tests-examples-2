package ru.yandex.metrika.api.management.client;

import java.util.List;
import java.util.Optional;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingStatus;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingType;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingMetadataService;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStoreService;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.collection.IsCollectionWithSize.hasSize;
import static org.mockito.Matchers.anyInt;
import static org.mockito.Matchers.anyLong;
import static org.mockito.Matchers.anyObject;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration
@WebAppConfiguration
public class ExpenseUploadingControllerFindTest {

    private static final String URI_PREFIX = "/management/v1/counter/{counter}/expense/";
    private static final int COUNTER_ID = 41292484;
    private static final int UPLOADING_ID = 1;
    private static final ExpenseUploading EXPENSE_UPLOADING = new ExpenseUploading(
            1, COUNTER_ID, 1, "provider", "comment", "bucket", "key",
            ExpenseUploadingStatus.UPLOADED, ExpenseUploadingType.EXPENSES);

    @Autowired
    private WebApplicationContext wac;

    private MockMvc mockMvc;

    @Before
    public void setup() {
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .build();
    }

    @Test
    public void returnsListOfUploadingsWhenFindAllIsInvoked() throws Exception {
        MvcResult result = mockMvc.perform(get(URI_PREFIX + "uploadings", COUNTER_ID)).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.uploadings", hasSize(1)))
                .andExpect(jsonPath("$.uploadings[0].status", is(ExpenseUploadingStatus.UPLOADED.toString())));
    }

    @Test
    public void returnsUploadingsWhenFindByIdIsInvoked() throws Exception {
        MvcResult result = mockMvc.perform(get(URI_PREFIX + "uploading/{uploadingId}", COUNTER_ID, UPLOADING_ID)).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.uploading.status", is(ExpenseUploadingStatus.UPLOADED.toString())));
    }

    @Configuration
    @Import(ExpenseUploadingControllerCommonContext.class)
    static class ContextConfiguration {

        @Bean
        public ExpenseUploadingMetadataService expenseUploadingMetadataService() {
            ExpenseUploadingMetadataService service = mock(ExpenseUploadingMetadataService.class);
            when(service.getUploadings(anyInt(), anyObject(), anyObject())).thenReturn(List.of(EXPENSE_UPLOADING));
            when(service.findUploading(anyInt(), anyLong())).thenReturn(Optional.of(EXPENSE_UPLOADING));
            return service;
        }

        @Bean
        public ExpenseUploadingStoreService expenseUploadingStoreService() {
            return mock(ExpenseUploadingStoreService.class);
        }
    }

}

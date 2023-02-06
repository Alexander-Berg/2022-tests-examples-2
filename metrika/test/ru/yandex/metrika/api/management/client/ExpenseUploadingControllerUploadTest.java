package ru.yandex.metrika.api.management.client;

import java.io.InputStream;
import java.util.Map;

import com.amazonaws.services.s3.model.ObjectListing;
import org.apache.http.impl.io.EmptyInputStream;
import org.jetbrains.annotations.Nullable;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.constructor.contr.FeatureServiceStub;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingStatus;
import ru.yandex.metrika.api.management.client.uploading.ExpenseCsvProcessService;
import ru.yandex.metrika.api.management.client.uploading.ExpenseCsvSampleData;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingMetadataService;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStoreService;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.spring.params.RenamingProcessor;
import ru.yandex.metrika.util.chunk.mds.MdsChunkStorage;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration
@WebAppConfiguration
public class ExpenseUploadingControllerUploadTest {

    public static final String UPLOAD_URI = "/management/v1/counter/{counter}/expense/upload";
    public static final String COUNTER_ID = "41292484";
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
    public void successWhenValidPostBody() throws Exception {
        MvcResult result = mockMvc.perform(
                getValidPost().content(ExpenseCsvSampleData.VALID_DATA)
        ).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.uploading.status", is(ExpenseUploadingStatus.UPLOADED.toString())));
    }

    @Test
    public void successWhenValidPostMultipart() throws Exception {
        MockMultipartFile csvFile = new MockMultipartFile("file",
                "expense.csv",
                "text/plain",
                ExpenseCsvSampleData.VALID_DATA.getBytes()
        );

        MvcResult result = mockMvc.perform(
                postWithRequiredParams(MockMvcRequestBuilders
                        .fileUpload(UPLOAD_URI, COUNTER_ID)
                        .file(csvFile))
        ).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.uploading.status", is(ExpenseUploadingStatus.UPLOADED.toString())));
    }

    @Test
    public void validErrorWhenInvalidColumnValue() throws Exception {
        MvcResult result = mockMvc.perform(
                getValidPost().content(ExpenseCsvSampleData.INVALID_DATE)
        ).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andDo(print())
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].errorType", is("invalid_uploading")))
                .andExpect(jsonPath("$.errors[0].location", isEmptyOrNullString()));
    }

    @Test
    public void validErrorWhenNoRequiredColumns() throws Exception {
        MvcResult result = mockMvc.perform(
                getValidPost().content(ExpenseCsvSampleData.INVALID_NO_REQUIRED_DATE_COLUMN)
        ).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].errorType", is("invalid_uploading")))
                .andExpect(jsonPath("$.errors[0].location", isEmptyOrNullString()));
    }

    private MockHttpServletRequestBuilder getValidPost() {
        return postWithRequiredParams(post(UPLOAD_URI, COUNTER_ID));
    }

    private MockHttpServletRequestBuilder postWithRequiredParams(MockHttpServletRequestBuilder post) {
        return post.param("provider", "some_provider")
                .param("comment", "some_comment");
    }

    @Configuration
    @Import(ExpenseUploadingControllerCommonContext.class)
    static class ContextConfiguration {

        @Autowired
        private LocaleDictionaries localeDictionaries;

        @Bean
        public ExpenseUploadingStoreService expenseUploadingStoreService() {
            return new ExpenseUploadingStoreService(
                    expenseUploadingMetadataService(),
                    expenseCsvProcessService(),
                    expenseMdsChunkStorage(),
                    expenseUploadingStorage(),
                    featureService()
            );
        }

        @Bean
        public ExpenseUploadingMetadataService expenseUploadingMetadataService() {
            ExpenseUploadingMetadataService mock = mock(ExpenseUploadingMetadataService.class);
            when(mock.getNextUploadingId()).thenReturn(1L);
            return mock;
        }

        @Bean
        public ExpenseCsvProcessService expenseCsvProcessService() {
            return new ExpenseCsvProcessService(currencyService(), countersDao(), localeDictionaries);
        }

        @Bean
        public MdsChunkStorage expenseMdsChunkStorage() {
            return new MockMdsChunkStorage();
        }

        @Bean
        public ExpenseUploadingStorage expenseUploadingStorage() {
            return new ExpenseUploadingStorage();
        }

        @Bean
        public CurrencyService currencyService() {
            CurrencyService currencyService = mock(CurrencyService.class);
            when(currencyService.getCurrenciesMap3Int()).thenReturn(Map.of("RUB", 643));
            return currencyService;
        }

        @Bean
        public CountersDao countersDao() {
            CountersDao countersDao = mock(CountersDao.class);
            when(countersDao.getCurrency(any())).thenReturn("RUB");
            return countersDao;
        }

        @Bean
        public LocalValidatorFactoryBean validator() {
            return new LocalValidatorFactoryBean();
        }

        @Bean
        public RenamingProcessor renamingProcessor() {
            return new RenamingProcessor(true);
        }

        @Bean
        public FeatureService featureService() {
            return new FeatureServiceStub();
        }

        private static class MockMdsChunkStorage implements MdsChunkStorage {

            @Override
            public void store(InputStream content, String key) {
                IOUtils.drainStream(content);
            }

            @Override
            public InputStream load(String bucket, String key) {
                return EmptyInputStream.INSTANCE;
            }

            @Override
            public String getBucket() {
                return "";
            }

            @Override
            public void remove(String key) {

            }

            @Override
            public boolean checkExistence(String key) {
                return true;
            }

            @Override
            public ObjectListing listNextBatch(@Nullable ObjectListing previousListing, Integer batchSize) {
                return null;
            }
        }
    }
}

package ru.yandex.metrika.cdp.api.tests.medium.datacontroller;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import org.junit.Before;
import org.junit.Test;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithUserDetails;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.web.WebAppConfiguration;

import ru.yandex.metrika.cdp.api.spring.CdpApiTestConfig;
import ru.yandex.metrika.cdp.api.tests.medium.AbstractCdpApiTest;
import ru.yandex.metrika.cdp.api.tests.medium.service.dataservice.AbstractDataServiceTest;
import ru.yandex.metrika.cdp.api.users.TestUsers;
import ru.yandex.metrika.cdp.api.validation.builders.ContactRowBuilder;
import ru.yandex.metrika.cdp.api.validation.builders.OrderRowBuilder;
import ru.yandex.metrika.cdp.common.CdpDateTimeUtils;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.frontend.data.wrappers.ContactRowsListWrapper;
import ru.yandex.metrika.cdp.frontend.data.wrappers.OrderRowsListWrapper;
import ru.yandex.metrika.util.io.IOUtils;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.cdp.api.tests.medium.service.dataservice.AbstractDataServiceTest.CONTACT_COLUMNS_MAPPING;
import static ru.yandex.metrika.cdp.api.tests.medium.service.dataservice.AbstractDataServiceTest.ORDER_COLUMNS_MAPPING;

@ContextConfiguration(classes = CdpApiTestConfig.class)
@WebAppConfiguration
@WithUserDetails(TestUsers.SIMPLE_USER_NAME)
public class DataControllerUploadTest extends AbstractCdpApiTest {

    private static final String PATH_TEMPLATE = "/cdp/api/v1/counter/{counterId}/data/{entity}";

    private ObjectMapper objectMapper;

    private int counterId;

    @Before
    @Override
    public void setUp() throws Exception {
        super.setUp();
        // preparing counter_id
        counterId = createCounter();

        // getting object mapper
        objectMapper = getObjectMapper().copy();
        var localDateTimeSerializer = new SimpleModule();
        localDateTimeSerializer.addSerializer(LocalDateTime.class,
                new LocalDateTimeSerializer(CdpDateTimeUtils.dateTimeFormatters.stream().findFirst().get().getValue()));
        objectMapper.registerModule(localDateTimeSerializer);
    }

    @Test
    public void testUploadContactsJson() throws Exception {
        mockMvc.perform(
                post(PATH_TEMPLATE, counterId, "contacts")
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .content(objectMapper.writeValueAsString(getContactRowsListWrapper()))
                        .queryParam("merge_mode", "save")
        ).andExpect(status().isOk());
    }

    @Test
    public void testUploadContactsCsv() throws Exception {
        byte[] fileContent = IOUtils
                .resourceAsString(AbstractDataServiceTest.class, "./csv/test_contacts.csv").getBytes();
        mockMvc.perform(
                multipart(PATH_TEMPLATE, counterId, "contacts")
                        .file("file", fileContent)
                        .contentType(MediaType.MULTIPART_FORM_DATA_VALUE)
                        .queryParam("merge_mode", "save")
                        .queryParam("columns_mapping", CONTACT_COLUMNS_MAPPING)
                        .queryParam("delimiter_type", "SEMICOLON")
        ).andExpect(status().isOk());
    }

    @Test
    public void testUploadOrdersJson() throws Exception {
        mockMvc.perform(
                post(PATH_TEMPLATE, counterId, "orders")
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .content(objectMapper.writeValueAsString(getOrderRowsListWrapper()))
                        .queryParam("merge_mode", "save")
        ).andExpect(status().isOk());
    }

    @Test
    public void testUploadOrdersCsv() throws Exception {
        byte[] fileContent = IOUtils
                .resourceAsString(AbstractDataServiceTest.class, "./csv/test_orders.csv").getBytes();
        mockMvc.perform(
                multipart(PATH_TEMPLATE, counterId, "orders")
                        .file("file", fileContent)
                        .contentType(MediaType.MULTIPART_FORM_DATA_VALUE)
                        .queryParam("merge_mode", "save")
                        .queryParam("columns_mapping", ORDER_COLUMNS_MAPPING)
                        .queryParam("delimiter_type", "SEMICOLON")
        ).andExpect(status().isOk());
    }


    @Test
    public void testUploadContactsNegative() throws Exception {
        mockMvc.perform(
                post(PATH_TEMPLATE, counterId, "contacts")
                        .contentType(MediaType.APPLICATION_PDF_VALUE)
                        .content(objectMapper.writeValueAsString(getContactRowsListWrapper()))
                        .queryParam("merge_mode", "save")
        ).andExpect(status().isBadRequest());
    }

    @Test
    public void testUploadOrdersNegative() throws Exception {
        mockMvc.perform(
                post(PATH_TEMPLATE, counterId, "orders")
                        .contentType(MediaType.APPLICATION_XML_VALUE)
                        .content(objectMapper.writeValueAsString(getOrderRowsListWrapper()))
                        .queryParam("merge_mode", "save")
        ).andExpect(status().isBadRequest());
    }

    private OrderRowsListWrapper getOrderRowsListWrapper() {
        var ordersWrapper = new OrderRowsListWrapper();
        ordersWrapper.setOrders(
                List.of(
                        OrderRowBuilder.anOrderRow()
                                .withId("id")
                                .withClientUniqId("uniqId")
                                .withClientType(ClientType.CONTACT)
                                .withOrderStatus("some")
                                .withCounterId(counterId)
                                .withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(10))
                                .build()
                ));
        return ordersWrapper;
    }

    private ContactRowsListWrapper getContactRowsListWrapper() {
        var contactsWrapper = new ContactRowsListWrapper();
        contactsWrapper.setContacts(
                List.of(
                        ContactRowBuilder.aContactRow()
                                .withUniqId("uniqId")
                                .withCounterId(counterId).build()));
        return contactsWrapper;
    }

}

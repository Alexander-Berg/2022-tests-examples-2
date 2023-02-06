package ru.yandex.metrika.cdp.api.tests.medium.schemacontroller;

import java.util.Collection;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithUserDetails;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.web.WebAppConfiguration;

import ru.yandex.metrika.cdp.api.spring.CdpApiTestConfig;
import ru.yandex.metrika.cdp.api.tests.medium.AbstractCdpApiTest;
import ru.yandex.metrika.cdp.api.users.TestUsers;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.SystemEntityNamespace;
import ru.yandex.metrika.cdp.frontend.schema.external.AllAttributesListWrapper;
import ru.yandex.metrika.cdp.frontend.schema.external.AttributesListWrapper;

import static java.util.stream.Collectors.toList;
import static org.assertj.core.util.Arrays.array;
import static org.hamcrest.Matchers.contains;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.cdp.dto.schema.AttributeType.DATE;
import static ru.yandex.metrika.cdp.dto.schema.AttributeType.DATETIME;
import static ru.yandex.metrika.cdp.dto.schema.AttributeType.EMAIL;
import static ru.yandex.metrika.cdp.dto.schema.AttributeType.NUMERIC;
import static ru.yandex.metrika.cdp.dto.schema.AttributeType.TEXT;


@RunWith(Parameterized.class)
@ContextConfiguration(classes = CdpApiTestConfig.class)
@WebAppConfiguration
public class SchemaControllerAttributesCreationTest extends AbstractCdpApiTest {

    private static final String PATH_TEMPLATE = "/cdp/api/v1/counter/{counterId}/schema/attributes?entity_type={entity_type}";

    private ObjectMapper objectMapper;

    private int counterId;

    @Parameter(value = 0)
    public Attribute attribute;

    @Parameter(value = 1)
    public String entityType;

    @Parameter(value = 2)
    public String name; // just for test name

    private static Attribute createAttribute(AttributeType attributeType, boolean multivalued) {
        return new Attribute(
                "testAttr_" + attributeType.getName() + "_" + multivalued,
                "Test" + (multivalued ? " multivalue" : "") + " attribute with type '" + attributeType.getName() + "'",
                attributeType,
                multivalued
        );
    }

    @Parameters(name = "{index}: Creating {2} for entity {1}")
    public static Collection<Object[]> parameters() {
        return Lists.cartesianProduct(
                List.of(NUMERIC, DATE, DATETIME, EMAIL, TEXT),
                List.of(true, false),
                List.of(SystemEntityNamespace.CONTACT.name(), SystemEntityNamespace.ORDER.name())
        ).stream()
                .map(objs -> {
                            var attribute = createAttribute((AttributeType) objs.get(0), (Boolean) objs.get(1));
                            return array(
                                    attribute,
                                    objs.get(2),
                                    attribute.getHumanized()
                            );
                        }
                )
                .collect(toList());
    }

    @Before
    @Override
    public void setUp() throws Exception {
        super.setUp();
        // preparing counter_id
        counterId = createCounter();
        // getting object mapper
        objectMapper = getObjectMapper();
    }

    @Test
    @WithUserDetails(TestUsers.SIMPLE_USER_NAME)
    public void createAttributeTest() throws Exception {

        mockMvc.perform(
                post(PATH_TEMPLATE, counterId, entityType)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(new AttributesListWrapper(List.of(attribute))))
        ).andExpect(status().isOk());

        var json = mockMvc.perform(get(PATH_TEMPLATE, counterId, entityType))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        var allAttributesListWrapper = objectMapper.readValue(json, AllAttributesListWrapper.class);

        Assert.assertThat(allAttributesListWrapper.getCustomAttributes(), contains(attribute));
    }

}

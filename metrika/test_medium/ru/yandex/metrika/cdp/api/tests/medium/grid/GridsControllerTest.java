package ru.yandex.metrika.cdp.api.tests.medium.grid;

import java.util.List;
import java.util.Map;

import javax.annotation.Nonnull;

import org.junit.Before;
import org.junit.Test;
import org.springframework.security.test.context.support.WithUserDetails;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import ru.yandex.metrika.api.constructor.response.ConstructorResponseStaticObject;
import ru.yandex.metrika.cdp.api.spring.CdpApiTestConfig;
import ru.yandex.metrika.cdp.api.tests.medium.AbstractCdpApiTest;
import ru.yandex.metrika.cdp.api.tests.medium.CdpApiTestSetup;
import ru.yandex.metrika.cdp.api.users.TestUsers;
import ru.yandex.metrika.segments.core.query.parts.AttributeKeys;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;

import static java.util.stream.Collectors.toList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.segments.site.bundles.cdp.CustomAttributeBuilders.getDateAttrName;
import static ru.yandex.metrika.segments.site.bundles.cdp.CustomAttributeBuilders.getNumberAttrName;
import static ru.yandex.metrika.segments.site.bundles.cdp.CustomAttributeBuilders.getStringMultiAttrName;
import static ru.yandex.metrika.util.StringUtil.smartUncapitalize;

@ContextConfiguration(classes = CdpApiTestConfig.class)
@WebAppConfiguration
@WithUserDetails(TestUsers.SIMPLE_USER_NAME)
public class GridsControllerTest extends AbstractCdpApiTest {

    private static final String PATH_TEMPLATE = "/cdp/api/v1/data/clients_grid?dimensions=cdp:cn:CDPUID,cdp:cn:externalHardID&ids={counterId}";
    private static final String CUSTOM_DIMENSIONS_PATH_TEMPLATE = "/cdp/api/v1/data/clients_grid?ids={counterId}&dimensions={dimensions}";
    private static final String FILTERS_TEMPLATE = "&filters={filters}";

    private int counterId;

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        counterId = createCounter();
        CdpApiTestSetup.prepareClickhouse(Map.of("counter_id", counterId));
    }

    @Test
    public void testGridWorking() throws Exception {
        var json = mockMvc.perform(MockMvcRequestBuilders.get(PATH_TEMPLATE, counterId))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        var constructorResponseStaticObject = getObjectMapper().readValue(json, ConstructorResponseStaticObject.class);
        assertEquals(44, constructorResponseStaticObject.getData().size());
    }

    @Test
    public void testNameTruncation() throws Exception {
        var nameAttr = contactAttribute("Name");
        var json = mockMvc.perform(MockMvcRequestBuilders.get(CUSTOM_DIMENSIONS_PATH_TEMPLATE, counterId, nameAttr))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        var names = extractColumn(
                getObjectMapper().readValue(json, ConstructorResponseStaticObject.class),
                nameAttr
        );
        //from "Oleg Pupkin1", "Dog Anna", "gegw", "1", "Oleg Ddsf FFF"
        var truncatedNamesList = List.of("Oleg P.", "Dog A.", "gegw", "1", "Oleg D.");

        assertTrue(names.containsAll(truncatedNamesList));
    }

    @Test
    public void testNameSegmentation() throws Exception {
        var nameAttr = contactAttribute("Name");
        var json = mockMvc.perform(
                MockMvcRequestBuilders.get(
                        CUSTOM_DIMENSIONS_PATH_TEMPLATE + FILTERS_TEMPLATE,
                        counterId,
                        nameAttr,
                        nameAttr + " == 'Anna I.'"
                ))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        var constructorResponseStaticObject = getObjectMapper().readValue(json, ConstructorResponseStaticObject.class);
        assertEquals(2, constructorResponseStaticObject.getData().size());
        assertEquals(
                List.of("203", "407"),
                extractHardIds(constructorResponseStaticObject)
        );
    }

    @Test
    public void testMultivalueAttrFiltration() throws Exception {
        var attrName = contactAttribute(getStringMultiAttrName("novoelilovoe"));
        var json = mockMvc.perform(MockMvcRequestBuilders.get(PATH_TEMPLATE + FILTERS_TEMPLATE, counterId, attrName + " == 'рвапароуап'"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        var constructorResponseStaticObject = getObjectMapper().readValue(json, ConstructorResponseStaticObject.class);
        assertEquals(2, constructorResponseStaticObject.getData().size());

        assertEquals(
                List.of("8", "18"),
                extractHardIds(constructorResponseStaticObject)
        );
    }

    @Test
    public void testFiltrationByDateAttribute() throws Exception {
        var attrName = contactAttribute(getDateAttrName("Datanachala"));
        var json = mockMvc.perform(MockMvcRequestBuilders.get(PATH_TEMPLATE + FILTERS_TEMPLATE, counterId, attrName + " <= '2019-10-29'"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        var constructorResponseStaticObject = getObjectMapper().readValue(json, ConstructorResponseStaticObject.class);
        assertEquals(1, constructorResponseStaticObject.getData().size());

        assertEquals(
                List.of("6"),
                extractHardIds(constructorResponseStaticObject)
        );
    }

    @Test
    public void testCustomAttrValueFetch() throws Exception {
        var idAttrName = contactAttribute(getNumberAttrName("ID"));
        var json = mockMvc.perform(MockMvcRequestBuilders.get(CUSTOM_DIMENSIONS_PATH_TEMPLATE + FILTERS_TEMPLATE , counterId, idAttrName, "cdp:cn:externalHardID == '14'"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        var constructorResponseStaticObject = getObjectMapper().readValue(json, ConstructorResponseStaticObject.class);
        assertEquals(1, constructorResponseStaticObject.getData().size());

        assertEquals(
                List.of("14.0"),
                extractColumn(constructorResponseStaticObject, idAttrName)
        );
    }

    @Nonnull
    private List<Object> extractHardIds(ConstructorResponseStaticObject constructorResponseStaticObject) {
        return extractColumn(constructorResponseStaticObject, "cdp:cn:externalHardID");
    }

    @Nonnull
    private List<Object> extractColumn(ConstructorResponseStaticObject constructorResponseStaticObject, String name) {
        var hardIdIndex = constructorResponseStaticObject.getQuery().getDimensions().indexOf(name);
        return extractColumn(constructorResponseStaticObject, hardIdIndex);
    }

    @Nonnull
    private List<Object> extractColumn(ConstructorResponseStaticObject constructorResponseStaticObject, int columnIndex) {
        return constructorResponseStaticObject.getData()
                .stream()
                .map(row -> row.getDimensions().get(columnIndex).get(AttributeKeys.NAME))
                .collect(toList());
    }

    private static String contactAttribute(String attrName) {
        return TableSchemaSite.CONTACTS.getNamespace() + smartUncapitalize(attrName);
    }
}

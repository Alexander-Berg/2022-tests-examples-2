package ru.yandex.metrika.mobmet.profiles;

import java.io.IOException;
import java.util.Collection;
import java.util.List;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.profiles.service.sessions.ProfileEventParsedParamsAssembler;

import static java.util.Arrays.asList;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;

/**
 * Проверяем, как {@link ProfileEventParsedParamsAssembler} справляется с тем, чтобы собрать
 * параметры клиентского события в JSON из набора путей от корня до листьев.
 */
@RunWith(Parameterized.class)
public class ProfileEventParsedParamsAssemblerTest {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final ProfileEventParsedParamsAssembler jsonAssembler = new ProfileEventParsedParamsAssembler();

    @Parameterized.Parameter
    public List<List<String>> paramsLevels;

    @Parameterized.Parameter(1)
    public String expectedJson;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> cases() {
        return asList(
                new Object[]{
                        asList(
                                asList("key1", "value1", null, null, null),
                                asList("key2", "value2", null, null, null),
                                asList("key3", "value3", null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key1\" : \"value1\"," +
                                "   \"key2\" : \"value2\"," +
                                "   \"key3\" : \"value3\"" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key1", "subkey1", "value1", null, null),
                                asList("key1", "subkey2", "value2", null, null),
                                asList("key2", "subkey1", "value3", null, null),
                                asList("key2", "subkey2", "value4", null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key1\" : {" +
                                "       \"subkey1\" : \"value1\"," +
                                "       \"subkey2\" : \"value2\"" +
                                "   }," +
                                "   \"key2\" : {" +
                                "       \"subkey1\" : \"value3\"," +
                                "       \"subkey2\" : \"value4\"" +
                                "   }" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key", "subkey1", "value1", null, null),
                                asList("key", "subkey2", "value2", null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key\" : {" +
                                "           \"subkey1\" : \"value1\"," +
                                "           \"subkey2\" : \"value2\"" +
                                "   }" +
                                "}"
                },
                new Object[]{
                        emptyList(),
                        "" +
                                "{}"
                },
                new Object[]{
                        singletonList(
                                asList("key", null, null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key\" : \"\"" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key1", null, null, null, null),
                                asList("key2", "not_empty", null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key1\" : \"\"," +
                                "   \"key2\" : \"not_empty\"" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key1", "not_empty", null, null, null),
                                asList("key2", null, null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key1\" : \"not_empty\"," +
                                "   \"key2\" : \"\"" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key", "subkey1", null, null, null),
                                asList("key", "subkey2", "not_empty", null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key\" : {" +
                                "       \"subkey1\" : \"\"," +
                                "       \"subkey2\" : \"not_empty\"" +
                                "   }" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key", "subkey1", "not_empty", null, null),
                                asList("key", "subkey2", null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key\" : {" +
                                "       \"subkey1\" : \"not_empty\"," +
                                "       \"subkey2\" : \"\"" +
                                "   }" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("WidgetNames", "Крэши", null, null, null),
                                asList("WidgetNames", "Новые пользователи", null, null, null),
                                asList("WidgetNames", "Партнеры", null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"WidgetNames\" : {" +
                                "       \"Крэши\" : \"\"," +
                                "       \"Новые пользователи\" : \"\"," +
                                "       \"Партнеры\" : \"\"" +
                                "   }" +
                                "}"
                },
                new Object[]{
                        asList(
                                asList("key1", null, null, null, null),
                                asList("key2", null, null, null, null),
                                asList("key3", null, null, null, null)
                        ),
                        "" +
                                "{" +
                                "   \"key1\" : \"\"," +
                                "   \"key2\" : \"\"," +
                                "   \"key3\" : \"\"" +
                                "}"
                }
        );
    }

    @Test
    public void testEventAttributesAssembled() throws IOException {
        String json = jsonAssembler.assembleToJson(paramsLevels);

        JsonNode actualTree = objectMapper.readTree(json);
        JsonNode expectedTree = objectMapper.readTree(expectedJson);

        assertEquals(expectedTree, actualTree);
    }
}

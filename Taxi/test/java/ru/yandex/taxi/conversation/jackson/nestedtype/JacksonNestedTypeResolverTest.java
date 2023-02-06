package ru.yandex.taxi.conversation.jackson.nestedtype;

import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.exc.InvalidTypeIdException;
import com.fasterxml.jackson.databind.type.CollectionType;
import com.fasterxml.jackson.databind.type.TypeFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.io.ResourceLoader;
import org.springframework.test.context.junit.jupiter.web.SpringJUnitWebConfig;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedDataMk1;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedDataMk2;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedId;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedType;
import ru.yandex.taxi.conversation.jackson.nestedtype.level0.NestedTypeLevel0;
import ru.yandex.taxi.conversation.jackson.nestedtype.level0.TypeL0Mk1;
import ru.yandex.taxi.conversation.jackson.nestedtype.level0.TypeL0Mk2;
import ru.yandex.taxi.conversation.jackson.nestedtype.level1.NestedTypeLevel1;
import ru.yandex.taxi.conversation.jackson.nestedtype.level1.TypeL1Mk1;
import ru.yandex.taxi.conversation.jackson.nestedtype.level1.TypeL1Mk2;
import ru.yandex.taxi.conversation.jackson.nestedtype.level2.NestedTypeLevel2;
import ru.yandex.taxi.conversation.jackson.nestedtype.level2.TypeL2Mk1;
import ru.yandex.taxi.conversation.jackson.nestedtype.level2.TypeL2Mk2;
import ru.yandex.taxi.conversation.jackson.nestedtype.negative.NestedTypeMissed;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static ru.yandex.taxi.conversation.jackson.nestedtype.JacksonNestedTypeTestConfig.JACKSON_NESTED_TYPE_TEST_MAPPER_NAME;

@SpringJUnitWebConfig(classes = JacksonNestedTypeTestConfig.class)
public class JacksonNestedTypeResolverTest {

    @Autowired
    @Qualifier(JACKSON_NESTED_TYPE_TEST_MAPPER_NAME)
    private ObjectMapper objectMapper;

    @Autowired
    private ResourceLoader resourceLoader;

    @Test
    public void deserializationLevel0() throws Exception {

        var resource = resourceLoader.getResource("classpath:jackson/nestedtype/nested-type-level0.json");

        List<NestedType> referenceList = List.of(
                new TypeL0Mk1("mk1", null, "Mark 1", new NestedDataMk1("asd1", "UTF-8")),
                new TypeL0Mk2("mk2", new NestedId("mk2_l1", "mk2 level1"), 999L, new NestedDataMk2("qwerty", 100500L)),
                new TypeL0Mk1("mk1", new NestedId("mk1_l1", "mk1 level1", new NestedId("mk1_l2", "mk1 level2")),
                        "Mark 1", new NestedDataMk1("asd2", "UTF-8")));

        CollectionType type = TypeFactory.defaultInstance().constructCollectionType(List.class, NestedTypeLevel0.class);
        List<NestedType> result = objectMapper.readValue(resource.getFile(), type);

        assertEquals(3, result.size());
        assertEquals(referenceList, result);
    }

    @Test
    public void deserializationLevel1() throws Exception {

        var resource = resourceLoader.getResource("classpath:jackson/nestedtype/nested-type-level1.json");

        List<NestedType> referenceList = List.of(
                new TypeL1Mk1("mk1", new NestedId("mk1_l1", "mk1 level1"),
                        "Mark 1", new NestedDataMk1("asd1", "UTF-8")),
                new TypeL1Mk2("mk2", new NestedId("mk2_l1", "mk2 level1"),
                        999L, new NestedDataMk2("qwerty", 100500L)),
                new TypeL1Mk1("mk1", new NestedId("mk1_l1", "mk1 level1", new NestedId("mk1_l2", "mk1 level2")),
                        "Mark 1", new NestedDataMk1("asd2", "UTF-8")));

        CollectionType type = TypeFactory.defaultInstance().constructCollectionType(List.class, NestedTypeLevel1.class);
        List<NestedType> result = objectMapper.readValue(resource.getFile(), type);

        assertEquals(3, result.size());
        assertEquals(referenceList, result);
    }

    @Test
    public void deserializationLevel2() throws Exception {

        var resource = resourceLoader.getResource("classpath:jackson/nestedtype/nested-type-level2.json");

        List<NestedType> referenceList = List.of(
                new TypeL2Mk1("mk1", new NestedId("mk1_l1", "mk1 level1", new NestedId("mk1_l2", "mk1 level2")),
                        "Mark 1", new NestedDataMk1("asd1", "UTF-8")),
                new TypeL2Mk2("mk2", new NestedId("mk2_l1", "mk2 level1", new NestedId("mk2_l2", "mk2 level2")),
                        999L, new NestedDataMk2("qwerty", 100500L)));

        CollectionType type = TypeFactory.defaultInstance().constructCollectionType(List.class, NestedTypeLevel2.class);
        List<NestedType> result = objectMapper.readValue(resource.getFile(), type);

        assertEquals(2, result.size());
        assertEquals(referenceList, result);
    }

    @Test
    public void deserializationMissedProperty() {
        var resource = resourceLoader.getResource("classpath:jackson/nestedtype/nested-type-level2.json");

        CollectionType type = TypeFactory.defaultInstance().constructCollectionType(List.class, NestedTypeMissed.class);

        assertThrows(InvalidTypeIdException.class, () -> objectMapper.readValue(resource.getFile(), type));
    }

    @Test
    public void serialization() throws Exception {

        var reference = resourceLoader.getResource("classpath:jackson/nestedtype/nested-type-level2.json");

        List<NestedType> listToSerialize = List.of(
                new TypeL2Mk1("mk1", new NestedId("mk1_l1", "mk1 level1", new NestedId("mk1_l2", "mk1 level2")),
                        "Mark 1", new NestedDataMk1("asd1", "UTF-8")),
                new TypeL2Mk2("mk2", new NestedId("mk2_l1", "mk2 level1", new NestedId("mk2_l2", "mk2 level2")),
                        999L, new NestedDataMk2("qwerty", 100500L)));

        String jsonFromObject = objectMapper.writeValueAsString(listToSerialize);
        assertEquals(objectMapper.readTree(reference.getFile()), objectMapper.readTree(jsonFromObject));
    }
}

package ru.yandex.metrika.util.dao;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Type;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableMap;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.junit.Assert;
import org.junit.Test;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.any;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasEntry;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.instanceOf;
import static org.hamcrest.Matchers.not;

public class MetadataGeneratorTest {

    private final JdbcMetadataGenerator jdbcMetadataGenerator = new JdbcMetadataGenerator();

    @Test
    public void test() throws NoSuchFieldException, NoSuchMethodException {
        JdbcClassMeta<Entity> meta = jdbcMetadataGenerator.generateMeta(Entity.class);

        Assert.assertThat(meta, classMeta(
                "Entity",
                Entity.class,
                false,
                "entity",
                of("firstId", "secondId"),
                ImmutableMap.<String, Matcher<JdbcPropertyMeta>>builder()
                        .put("firstId", propertyMeta(
                                "firstId",
                                Entity.class.getDeclaredField("firstId"),
                                Entity.class.getDeclaredMethod("getFirstId"),
                                Entity.class.getDeclaredMethod("setFirstId", int.class),
                                "first_id",
                                true,
                                false,
                                int.class
                        ))
                        .put("secondId", propertyMeta(
                                "secondId",
                                Entity.class.getDeclaredField("secondId"),
                                Entity.class.getDeclaredMethod("getSecondId"),
                                Entity.class.getDeclaredMethod("setSecondId", int.class),
                                "second_id",
                                true,
                                false,
                                int.class
                        ))
                        .put("name", propertyMeta(
                                "name",
                                Entity.class.getDeclaredField("name"),
                                Entity.class.getDeclaredMethod("getName"),
                                Entity.class.getDeclaredMethod("setName", String.class),
                                "name",
                                false,
                                false,
                                String.class
                        ))
                        .put("custom", propertyMeta(
                                "custom",
                                Entity.class.getDeclaredField("custom"),
                                Entity.class.getDeclaredMethod("getCustom"),
                                Entity.class.getDeclaredMethod("setCustom", String.class),
                                "custom_name",
                                false,
                                false,
                                String.class
                        ))
                        .put("readOnly", propertyMeta(
                                "readOnly",
                                Entity.class.getDeclaredField("readOnly"),
                                Entity.class.getDeclaredMethod("getReadOnly"),
                                Entity.class.getDeclaredMethod("setReadOnly", String.class),
                                "read_only",
                                false,
                                true,
                                String.class
                        ))
                        .put("convert", propertyMeta(
                                "convert",
                                Entity.class.getDeclaredField("convert"),
                                Entity.class.getDeclaredMethod("getConvert"),
                                Entity.class.getDeclaredMethod("setConvert", CustomProperty.class),
                                "convert",
                                false,
                                false,
                                String.class,
                                instanceOf(CustomPropertyConverter.class)
                        ))
                        .put("genericConvert", propertyMeta(
                                "genericConvert",
                                Entity.class.getDeclaredField("genericConvert"),
                                Entity.class.getDeclaredMethod("getGenericConvert"),
                                Entity.class.getDeclaredMethod("setGenericConvert", Map.class),
                                "generic_convert",
                                false,
                                false,
                                String.class,
                                allOf(instanceOf(GenericPropertyConverter.class), hasProperty(
                                        "propertyType",
                                        equalTo(Entity.class.getDeclaredField("genericConvert").getGenericType())
                                ))
                        ))
                        .build(),
                of("trans")
        ));
    }

    public static Matcher<JdbcClassMeta> classMeta(
            String name,
            Class<?> clazz,
            boolean autoGeneratedId,
            String tableName,
            Collection<String> idPropertyNames,
            Map<String, Matcher<JdbcPropertyMeta>> propertyMatchers,
            List<String> transientProperties
    ) {
        return allOf(
                hasProperty("name", equalTo(name)),
                hasProperty("clazz", equalTo(clazz)),
                hasProperty("autoGeneratedId", equalTo(autoGeneratedId)),
                hasProperty("tableName", equalTo(tableName)),
                hasProperty("idPropertyNames", contains(
                        idPropertyNames.stream()
                                .map(Matchers::equalTo)
                                .collect(Collectors.toList())
                )),
                hasProperty("properties", allOf(
                        propertyMatchers.entrySet().stream()
                                .map(entry -> hasEntry(equalTo(entry.getKey()), entry.getValue()))
                                .collect(Collectors.toList())
                )),
                hasProperty("properties", allOf(
                        transientProperties.stream()
                                .map(property -> not(hasEntry(equalTo(property), any(JdbcPropertyMeta.class))))
                                .collect(Collectors.toList())
                ))
        );
    }

    public static Matcher<JdbcPropertyMeta> propertyMeta(
            String name,
            Field field,
            Method getter,
            Method setter,
            String columnName,
            boolean isId,
            boolean isReadOnly,
            Class<?> jdbcType
    ) {
        return propertyMeta(name, field, getter, setter, columnName, isId, isReadOnly, jdbcType, equalTo(null));
    }

    public static Matcher<JdbcPropertyMeta> propertyMeta(
            String name,
            Field field,
            Method getter,
            Method setter,
            String columnName,
            boolean isId,
            boolean isReadOnly,
            Class<?> jdbcType,
            Matcher<PropertyConverter<?, ?>> converterMatcher
    ) {
        return allOf(
                hasProperty("name", equalTo(name)),
                hasProperty("field", equalTo(field)),
                hasProperty("getter", equalTo(getter)),
                hasProperty("setter", equalTo(setter)),
                hasProperty("columnName", equalTo(columnName)),
                hasProperty("id", equalTo(isId)),
                hasProperty("readOnly", equalTo(isReadOnly)),
                hasProperty("jdbcType", equalTo(jdbcType)),
                hasProperty("converter", converterMatcher)
        );
    }

    @Table(Entity.TABLE_NAME)
    public static class Entity {

        public static final String TABLE_NAME = "entity";

        @Id
        private int firstId;

        @Id
        private int secondId;

        private String name;

        @Column("custom_name")
        private String custom;

        @Transient
        private String trans;

        @ReadOnly
        private String readOnly;

        @Convert(CustomPropertyConverter.class)
        private CustomProperty convert;

        @Convert(GenericPropertyConverter.class)
        private Map<String, List<String>> genericConvert;

        public int getFirstId() {
            return firstId;
        }

        public void setFirstId(int firstId) {
            this.firstId = firstId;
        }

        public int getSecondId() {
            return secondId;
        }

        public void setSecondId(int secondId) {
            this.secondId = secondId;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getCustom() {
            return custom;
        }

        public void setCustom(String custom) {
            this.custom = custom;
        }

        public String getTrans() {
            return trans;
        }

        public void setTrans(String trans) {
            this.trans = trans;
        }

        public String getReadOnly() {
            return readOnly;
        }

        public void setReadOnly(String readOnly) {
            this.readOnly = readOnly;
        }

        public CustomProperty getConvert() {
            return convert;
        }

        public void setConvert(CustomProperty convert) {
            this.convert = convert;
        }

        public Map<String, List<String>> getGenericConvert() {
            return genericConvert;
        }

        public void setGenericConvert(Map<String, List<String>> genericConvert) {
            this.genericConvert = genericConvert;
        }
    }

    public record CustomProperty(int a, int b) {
    }

    public static class CustomPropertyConverter implements PropertyConverter<CustomProperty, String> {


        @Override
        public String convertToJdbc(CustomProperty value) {
            return "1,2";
        }

        @Override
        public CustomProperty convertFromJdbc(String jdbcValue) {
            return new CustomProperty(1, 2);
        }
    }

    public static class GenericPropertyConverter implements PropertyConverter<Object, String> {

        private final Type propertyType;

        public GenericPropertyConverter(Type propertyType) {
            this.propertyType = propertyType;
        }

        @Override
        public String convertToJdbc(Object value) {
            return "a:[1,2];b:[3,4]";
        }

        @Override
        public Object convertFromJdbc(String jdbcValue) {
            return ImmutableMap.of(
                    "a", of("1", "2"),
                    "b", of("3", "4")
            );
        }

        public Type getPropertyType() {
            return propertyType;
        }
    }
}

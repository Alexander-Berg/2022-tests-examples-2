package ru.yandex.metrika.cdp.api.schema;

import java.lang.reflect.ParameterizedType;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

import javax.annotation.Nonnull;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.introspect.BeanPropertyDefinition;
import org.hamcrest.Matchers;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.cdp.api.AbstractTest;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.AttributesContainer;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.schema.ListItem;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.csv.CSVMetadataGenerator;
import ru.yandex.metrika.cdp.frontend.csv.CSVPropertyMeta;
import ru.yandex.metrika.cdp.frontend.csv.converter.anysetter.AttributesConversionContext;
import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;
import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;
import ru.yandex.metrika.cdp.frontend.data.rows.SimpleOrderRow;
import ru.yandex.metrika.cdp.frontend.schema.SystemAttributes;
import ru.yandex.metrika.cdp.frontend.schema.rows.ListItemRow;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;

import static java.util.stream.Collectors.toSet;

/**
 * Этот тест придуман для того, чтобы отлавливать расхождения в системных атрибутах между описанием в SchemaService и
 * реальными полями в DTO классах.
 * <p>
 * Известные костыли:
 * - типизация products для заказов нормально не обрабытывается, для него нет нормально AttributeType
 * - AttributeType.TEXT -> Enum - если один атрибут Enum а второй String - ок
 * - кейсы когда AttributeType.NUMERIC, а реальное поле конкретный Long или BigDecimal проверяются через isAssignableFrom,
 * что не очень точно.
 */
@RunWith(Parameterized.class)
public class SystemAttributesMatchingTest extends AbstractTest {

    private CSVMetadataGenerator<AttributesConversionContext> csvMetadataGenerator;
    private ObjectMapper objectMapper;

    @Before
    public void setUp() throws Exception {
        csvMetadataGenerator = CSVMetadataGenerator.customAnySetterGenerator(AttributesConversionContext.class);

        MetrikaApiMessageConverter metrikaApiMessageConverter = new MetrikaApiMessageConverter();
        metrikaApiMessageConverter.afterPropertiesSet();
        objectMapper = metrikaApiMessageConverter.getObjectMapper();
    }

    @Parameterized.Parameter
    public EntityNamespace entityNamespace;

    @Parameterized.Parameter(1)
    public Class<? extends AttributesContainer> clazz;

    @Parameterized.Parameter(2)
    public UploadingFormat uploadingFormat;

    @Parameterized.Parameters(name = "entity: {0}, class: {1}, format: {2}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[][]{
                        {EntityNamespace.CONTACT, ContactRow.class, UploadingFormat.CSV},
                        {EntityNamespace.CONTACT, ContactRow.class, UploadingFormat.JSON},
                        {EntityNamespace.ORDER, OrderRow.class, UploadingFormat.CSV},
                        {EntityNamespace.ORDER, OrderRow.class, UploadingFormat.JSON},
                        {EntityNamespace.customListNamespace("any"), ListItem.class, UploadingFormat.JSON},
                        {EntityNamespace.customListNamespace("any"), ListItemRow.class, UploadingFormat.CSV},
                        {EntityNamespace.SIMPLE_ORDER, SimpleOrderRow.class, UploadingFormat.CSV},
                        {EntityNamespace.PRODUCT, ListItem.class, UploadingFormat.JSON}
                }
        );
    }

    @Test
    public void testFieldsMatchContactCsv() {
        var systemAttributesNames = getSystemAttributesNames(entityNamespace);
        var columnNames = getNamesByType(clazz, uploadingFormat);
        Assert.assertThat(columnNames, Matchers.containsInAnyOrder(systemAttributesNames));
    }

    @Nonnull
    private AttributeDescription[] getSystemAttributesNames(EntityNamespace entityNamespace) {
        return Optional.ofNullable(SystemAttributes.get(entityNamespace))
                .stream()
                .flatMap(List::stream)
                .map(AttributeDescription::new)
                .toArray(AttributeDescription[]::new);
    }

    @Nonnull
    private Set<AttributeDescription> getNamesByType(Class<?> clazz, UploadingFormat format) {
        switch (format) {
            case CSV:
                return getCsvColumnNames(clazz);
            case JSON:
                return getJsonPropertyNames(clazz);
            default:
                throw new IllegalArgumentException("Can not get names for format " + format);
        }
    }

    @Nonnull
    private Set<AttributeDescription> getCsvColumnNames(Class<?> clazz) {
        return csvMetadataGenerator.generateMeta(clazz).getProperties().values()
                .stream()
                .map(AttributeDescription::new)
                .collect(toSet());
    }

    @Nonnull
    private Set<AttributeDescription> getJsonPropertyNames(Class<?> clazz) {
        var contactRowType = objectMapper.getTypeFactory().constructType(clazz);
        return objectMapper.getSerializationConfig().introspect(contactRowType).findProperties()
                .stream()
                // это не системный атрибут а просто контейнер для кастомных
                .filter(beanPropertyDefinition -> !beanPropertyDefinition.getName().equals("attribute_values"))
                .map(AttributeDescription::new)
                .collect(toSet());
    }

    private static final class AttributeDescription {

        private static Class<?> getDesiredClass(AttributeType type) {
            assert type.getGroup() == AttributeType.Group.PREDEFINED;
            if (type.equals(AttributeType.DATE)) {
                return LocalDate.class;
            }
            if (type.equals(AttributeType.DATETIME)) {
                return LocalDateTime.class;
            }
            if (type.equals(AttributeType.NUMERIC)) {
                return Number.class;
            }
            if (type.equals(AttributeType.EMAIL) || type.equals(AttributeType.TEXT)) {
                return String.class;
            }
            throw new IllegalArgumentException();
        }

        @Nonnull
        private final String name;
        @Nonnull
        private final Class<?> targetClass;
        private final boolean isMultivalue;

        private AttributeDescription(Attribute attribute) {
            this.name = attribute.getName();
            // пока не понятно как сделать лучше
            if (this.name.equals("products")) {
                this.targetClass = Map.class;
                this.isMultivalue = false;
            } else {
                this.targetClass = getDesiredClass(attribute.getType());
                this.isMultivalue = attribute.getMultivalued();
            }
        }

        private AttributeDescription(CSVPropertyMeta csvPropertyMeta) {
            name = csvPropertyMeta.getColumnName();
            var field = csvPropertyMeta.getField();
            if (Collection.class.isAssignableFrom(field.getType())) {
                targetClass = (Class<?>) ((ParameterizedType) field.getGenericType()).getActualTypeArguments()[0];
                isMultivalue = true;
            } else {
                targetClass = field.getType();
                isMultivalue = false;
            }
        }

        private AttributeDescription(BeanPropertyDefinition beanPropertyDefinition) {
            name = beanPropertyDefinition.getName();
            var annotatedField = beanPropertyDefinition.getField();
            if (annotatedField.getType().isCollectionLikeType()) {
                targetClass = annotatedField.getType().getContentType().getRawClass();
                isMultivalue = true;
            } else {
                targetClass = annotatedField.getType().getRawClass();
                isMultivalue = false;
            }
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            AttributeDescription that = (AttributeDescription) o;
            return isMultivalue == that.isMultivalue &&
                    name.equals(that.name) &&
                    // костылёк
                    (
                            targetClass.isAssignableFrom(that.targetClass) ||
                                    that.targetClass.isAssignableFrom(targetClass) ||
                                    (that.targetClass.isEnum() && targetClass.equals(String.class)) ||
                                    (targetClass.isEnum() && that.targetClass.equals(String.class))
                    );
        }

        @Override
        public int hashCode() {
            return Objects.hash(name, targetClass, isMultivalue);
        }

        @Override
        public String toString() {
            return "AttributeDescription{" +
                    "name='" + name + '\'' +
                    ", targetClass=" + targetClass +
                    ", isMultivalue=" + isMultivalue +
                    '}';
        }
    }
}

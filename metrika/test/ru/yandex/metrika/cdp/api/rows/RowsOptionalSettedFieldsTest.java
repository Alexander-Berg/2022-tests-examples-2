package ru.yandex.metrika.cdp.api.rows;

import java.beans.FeatureDescriptor;
import java.beans.PropertyDescriptor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.annotation.Nonnull;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

import com.fasterxml.jackson.annotation.JsonIgnore;
import org.apache.commons.beanutils.PropertyUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.cdp.common.FieldNames;
import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;
import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;
import ru.yandex.metrika.cdp.frontend.data.rows.SimpleOrderRow;
import ru.yandex.metrika.cdp.frontend.rows.AbstractRowWithAttributes;
import ru.yandex.metrika.util.ReflectionUtils2;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.collections.MapBuilder;

import static java.util.Comparator.comparing;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static org.junit.Assert.assertThat;

/**
 * Этот метод призван силами рефлекшена и своих падений заставлять людей соблюдать следующий инвариант для
 * перечисленных тут AbstractRowWithAttributes (сейчас только ContactRow, OrderRow и SimpleOrderRow):
 * Все опциональные пользовательские поля в своём setter-е должны вызывать метод {@link AbstractRowWithAttributes#optionalFieldSetted(String)},
 * с ожидаемым параметром, чтобы потом эта информация могла быть использована в cdp-core для мержа данных
 */
@RunWith(Parameterized.class)
public class RowsOptionalSettedFieldsTest {

    private static final Map<String, String> ORDER_FIELD_ID_MAP = MapBuilder.<String, String>builder()
            .put("cost", FieldNames.Order.COST)
            .put("products", FieldNames.Order.PRODUCTS)
            .put("finishDateTime", FieldNames.Order.FINISH_DATE_TIME)
            .put("revenue", FieldNames.Order.REVENUE)
            .put("updateDateTime", FieldNames.Order.UPDATE_DATE_TIME)
            .build();

    private static final Map<String, String> SIMPLE_ORDER_FIELD_ID_MAP = MapBuilder.<String, String>builder()
            .put("cost", FieldNames.Order.COST)
            .put("revenue", FieldNames.Order.REVENUE)
            .put("clientIds", FieldNames.Client.CLIENT_IDS)
            .put("phones", FieldNames.Client.PHONES)
            .put("phonesMd5", FieldNames.Client.PHONES_MD5)
            .put("emails", FieldNames.Client.EMAILS)
            .put("emailsMd5", FieldNames.Client.EMAILS_MD5)
            .build();

    private static final Map<String, String> CONTACT_FIELD_ID_MAP = MapBuilder.<String, String>builder()
            .put("phonesMd5", FieldNames.Client.PHONES_MD5)
            .put("phones", FieldNames.Client.PHONES)
            .put("clientIds", FieldNames.Client.CLIENT_IDS)
            .put("birthDate", FieldNames.Client.BIRTH_DATE)
            .put("createDateTime", FieldNames.Client.CREATE_DATE_TIME)
            .put("emails", FieldNames.Client.EMAILS)
            .put("emailsMd5", FieldNames.Client.EMAILS_MD5)
            .put("userIds", FieldNames.Client.CLIENT_USER_IDS)
            .put("name", FieldNames.Client.NAME)
            .put("companyUniqId", FieldNames.Client.PARENT_CDP_UID)
            .put("updateDateTime", FieldNames.Client.UPDATE_DATE_TIME)
            .build();

    private static final Map<Class<? extends AbstractRowWithAttributes<?>>, Map<String, String>> FIELD_ID_MAP_BY_CLASS = Map.of(
            ContactRow.class, CONTACT_FIELD_ID_MAP,
            OrderRow.class, ORDER_FIELD_ID_MAP,
            SimpleOrderRow.class, SIMPLE_ORDER_FIELD_ID_MAP
    );

    @Parameterized.Parameter
    public FieldInfo fieldInfo;

    @Parameterized.Parameters(name = "{index}: {0}")
    public static Collection<Object[]> createParameters() {
        var params = new ArrayList<FieldInfo>();
        for (var clazz : FIELD_ID_MAP_BY_CLASS.keySet()) {
            var descriptorMap = Stream.of(PropertyUtils.getPropertyDescriptors(clazz))
                    .collect(Collectors.toMap(FeatureDescriptor::getName, Function.identity()));

            var fieldMap = ReflectionUtils2.getAllDeclaredFields(clazz).stream()
                    .collect(Collectors.toMap(Field::getName, Function.identity()));

            descriptorMap.keySet().stream()
                    .filter(fieldMap::containsKey)
                    .filter(FIELD_ID_MAP_BY_CLASS.get(clazz)::containsKey)
                    .map(key -> new FieldInfo(clazz, descriptorMap.get(key), fieldMap.get(key), FIELD_ID_MAP_BY_CLASS.get(clazz).get(key)))
                    .filter(fi ->
                            !fi.field.isAnnotationPresent(NotNull.class)
                                    && !fi.field.isAnnotationPresent(NotBlank.class)
                                    && !fi.field.isAnnotationPresent(JsonIgnore.class)
                    )
                    .forEach(params::add);
        }
        params.sort(comparing(FieldInfo::toString));
        return F.map(params, fi -> new Object[]{fi});
    }

    @Test
    public void test() throws NoSuchMethodException, IllegalAccessException, InvocationTargetException, InstantiationException {
        var instance = fieldInfo.parentClass.getDeclaredConstructor().newInstance();
        var defaultValue = getDefaultValue(fieldInfo.field.getGenericType());
        fieldInfo.propertyDescriptor.getWriteMethod().invoke(instance, defaultValue);
        assertThat(instance.getSettedOptionalFields(), not(empty()));
        assertThat(instance.getSettedOptionalFields(), contains(fieldInfo.fieldId));
    }

    private static Object getDefaultValue(Type type) {
        if (type instanceof Class) {
            var clazz = (Class<?>) type;
            if (clazz.isEnum()) {
                return clazz.getEnumConstants()[0];
            }
            if (clazz.equals(String.class)) {
                return "string";
            }
            if (clazz.equals(LocalDate.class)) {
                return LocalDate.now();
            }
            if (clazz.equals(LocalDateTime.class)) {
                return LocalDateTime.now();
            }
            if (clazz.equals(Integer.class)) {
                return 1;
            }
            if (clazz.equals(Long.class)) {
                return 1L;
            }
            if (clazz.equals(BigDecimal.class)) {
                return BigDecimal.ONE;
            }
        }
        if (type instanceof ParameterizedType) {
            var parametrizedType = (ParameterizedType) type;
            if (parametrizedType.getRawType() instanceof Class) {
                var clazz = (Class<?>) parametrizedType.getRawType();
                if (clazz.equals(List.class)) {
                    var defaultValue = getDefaultValue(parametrizedType.getActualTypeArguments()[0]);
                    return List.of(defaultValue);
                }
                if (clazz.equals(Set.class)) {
                    var defaultValue = getDefaultValue(parametrizedType.getActualTypeArguments()[0]);
                    return Set.of(defaultValue);
                }
                if (clazz.equals(Map.class)) {
                    var defaultKey = getDefaultValue(parametrizedType.getActualTypeArguments()[0]);
                    var defaultValue = getDefaultValue(parametrizedType.getActualTypeArguments()[1]);
                    return Map.of(defaultKey, defaultValue);
                }
            }
        }
        throw new IllegalArgumentException("Can not provide default value for type " + type);
    }


    private static final class FieldInfo {
        @Nonnull
        private final Class<? extends AbstractRowWithAttributes<?>> parentClass;
        @Nonnull
        private final PropertyDescriptor propertyDescriptor;
        @Nonnull
        private final Field field;
        @Nonnull
        private final String fieldId;

        public FieldInfo(@Nonnull Class<? extends AbstractRowWithAttributes<?>> parentClass, @Nonnull PropertyDescriptor propertyDescriptor, @Nonnull Field field, @Nonnull String fieldId) {
            this.parentClass = parentClass;
            this.propertyDescriptor = propertyDescriptor;
            this.field = field;
            this.fieldId = fieldId;
        }

        @Override
        public String toString() {
            return parentClass.getSimpleName() + ": " + field.getName();
        }
    }
}

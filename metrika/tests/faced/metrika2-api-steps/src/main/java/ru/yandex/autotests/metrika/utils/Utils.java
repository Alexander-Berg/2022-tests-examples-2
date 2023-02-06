package ru.yandex.autotests.metrika.utils;

import ch.lambdaj.util.iterator.ResettableIteratorOnArray;
import com.google.common.collect.Maps;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.EnumUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.joda.time.DateTime;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;

import java.net.MalformedURLException;
import java.net.URL;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.*;
import java.util.function.BiFunction;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Throwables.propagate;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toMap;
import static org.apache.commons.lang3.StringUtils.isBlank;

/**
 * Created by proxeter on 06.08.2014.
 */
public class Utils {

    private static final Pattern NAME_WITHOUT_NS_REGEX = Pattern.compile("ym:.*:(.*)");
    public static final String DATE_FORMAT = "yyyy-MM-dd";
    public static final String JSON_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ssX";

    /**
     * Комбинирует две коллекции в коллекцию всех возможных пар элементов исходных коллекций.
     *
     * @param firsts  первая коллекция
     * @param seconds вторая коллекция
     * @return коллекция пар, пара - массив из двух элементов, для использования в качестве параметров тестов.
     */
    public static Collection<Object[]> makePairs(Collection firsts, Collection seconds) {
        ArrayList<Object[]> result = new ArrayList<>();

        for (Object first : firsts) {
            for (Object second : seconds) {
                result.add(new Object[]{first, second});
            }
        }

        return result;
    }

    public static Collection<Object[]> makePairs(Object first, Collection seconds) {
        return makePairs(singletonList(first), seconds);
    }

    public static Collection<Object[]> makePairs(Collection firsts, Object second) {
        return makePairs(firsts, singletonList(second));
    }

    public static Collection<List<String>> makeStringPairs(Collection<String> firsts, Collection<String> seconds) {
        ArrayList<List<String>> result = new ArrayList<>();

        for (String first : firsts) {
            for (String second : seconds) {
                result.add(asList(first, second));
            }
        }

        return result;
    }

    /**
     * Комбинирует две коллекции массивов в коллекцию массивов, полученных объединением всех возможных пар элементов
     * исходных коллекций.
     *
     * @param firsts  первая коллекция массивов
     * @param seconds вторая коллекция массивов
     * @return коллекция массивов, каждый из которых получен объединением массива из первой коллекции
     * и массива из второй.
     */
    public static Collection combineCollections(Iterable<Object[]> firsts, Iterable<Object[]> seconds) {
        ArrayList<Object[]> result = new ArrayList<>();

        for (Object[] first : firsts) {
            for (Object[] second : seconds) {
                result.add(ArrayUtils.addAll(first, second));
            }
        }

        return result;
    }

    public static <T> Collection<T> getDuplicates(Iterable<T> items) {
        Collection<T> duplicates = new ArrayList<>();
        Set<T> unique = new HashSet<>();
        for (T item : items) {
            if (unique.contains(item)) {
                duplicates.add(item);
            } else {
                unique.add(item);
            }
        }
        return duplicates;
    }

    public static DecimalFormat getDecimalFormat(int maxDigits) {
        DecimalFormat decimalFormat = new DecimalFormat("#.", DecimalFormatSymbols.getInstance(Locale.ROOT));
        decimalFormat.setMaximumFractionDigits(maxDigits);

        return decimalFormat;
    }

    public static <T, V> List<V> zip(List<T> first, List<T> second, BiFunction<T, T, V> zipper) {

        if (first.size() != second.size()) {
            throw new IllegalArgumentException(String.format("%s != %s", first.size(), second.size()));
        }
        List<V> result = new ArrayList<>();
        for (int i = 0; i < first.size(); i++) {
            result.add(zipper.apply(first.get(i), second.get(i)));
        }
        return result;
    }

    /**
     * Сшивает два списка списков в один. Каждый список результирующего списка является объединением двух списков
     *
     * @param first  первый список списков
     * @param second второй список списков
     * @param <T>    тип значений в списках
     * @return результирующий список списков
     */
    public static <T> List<List<T>> zip(List<List<T>> first, List<List<T>> second) {

        if (first.size() != second.size()) {
            throw new IllegalArgumentException(String.format("%s != %s", first.size(), second.size()));
        }

        List<List<T>> result = new ArrayList<>();

        int size = first.size();
        for (int i = 0; i < size; i++) {
            List<T> row = new ArrayList<>();
            row.addAll(first.get(i));
            row.addAll(second.get(i));
            result.add(row);
        }

        return result;
    }

    /**
     * Сшивает два Map<K, Set<T>> в один.
     * Каждое значение в результате есть объединение множеств из значений параметров
     *
     * @param first  первый Map K -> Set<T>
     * @param second второй Map K -> Set<T>
     * @param <K>    тип ключа
     * @param <T>    тип элемента Set из значения
     * @return объединенный Map
     */
    public static <K, T> Map<K, Set<T>> zip(Map<K, Set<T>> first, Map<K, Set<T>> second) {
        Map<K, Set<T>> result = Maps.newHashMap(first);
        for (Map.Entry<K, Set<T>> e : second.entrySet()) {
            if (!result.containsKey(e.getKey())) {
                result.put(e.getKey(), e.getValue());
            } else {
                result.get(e.getKey()).addAll(e.getValue());
            }
        }
        return result;
    }

    /**
     * Сшивает два Map<K, List<T>> в один.
     * Каждое значение в результате есть ре
     *
     * @param first  первый Map K -> List<T>
     * @param second второй Map K -> List<T>
     * @param <K>    тип ключа
     * @param <T>    тип элемента List из значения
     * @return объединенный Map
     */
    public static <K, T> Map<K, List<T>> zip(Map<K, List<T>> first, Map<K, List<T>> second, BiFunction<List<T>, List<T>, List<T>> zipper) {
        Map<K, List<T>> result = Maps.newHashMap();
        Set<K> keys = new HashSet<>(first.keySet());
        keys.addAll(second.keySet());
        for (K key : keys) {
            if (first.containsKey(key) && second.containsKey(key)) {
                result.put(key, zipper.apply(first.get(key), second.get(key)));
            } else if (first.containsKey(key)) {
                result.put(key, first.get(key));
            } else {
                result.put(key, second.get(key));
            }
        }
        return result;
    }

    public static Object extractDimensionValue(Map<String, ?> dimension) {
        return dimension.containsKey("id")
                ? dimension.get("id")
                : dimension.get("name");
    }

    public static String getDateAfterTomorrow() {
        return DateTime.now().plusDays(2).toString(DATE_FORMAT);
    }

    public static String getPlus7DaysDate() {
        return DateTime.now().plusDays(7).toString(DATE_FORMAT);
    }

    public static IFormParameters aggregate(IFormParameters... parameterses) {
        return new FreeFormParameters().append(parameterses);
    }

    public static IFormParameters aggregate(IFormParameters parameters, IFormParameters[] parameterses) {
        return new FreeFormParameters().append(parameters).append(parameterses);
    }

    /**
     * @return получает список значений перечисления и null в виде единого списка
     */
    public static <E extends Enum<E>> List<E> getEnumListWithNull(Class<E> enumClass) {
        List<E> enumList = EnumUtils.getEnumList(enumClass);
        enumList.add(null);
        return enumList;
    }

    /**
     * Экранирование строк для использования в выражении фильтра
     *
     * @param value строка для экранирования
     * @return экранированная строка
     */
    public static String escapeFilterValue(String value) {
        return value.replace("\\", "\\\\").replace("'", "\\'");
    }

    /**
     * преобразует значение в строку для использования в фильтре.
     *
     * @param value значение
     * @return строка, если исходное значение было числовым, то одиночными кавычками не обрамляется
     */
    public static String wrapFilterValue(Object value) {
        String valueAsString = escapeFilterValue(Objects.toString(value, "null"));

        if (value != null && !(value instanceof Number)) {
            valueAsString = "'" + valueAsString + "'";
        }

        return valueAsString;
    }

    /**
     * Действует, как Lambda.flatten, но сохраняет null'ы
     *
     * @param iterable исходный контейнер
     * @return преобразованный контейнер
     */
    public static <T> List<T> flatten(Object iterable) {
        return flattenIterator(iterable);
        //return Lambda.flatten(iterable);
    }

    public static <T> List<T> flattenList(List<List<T>> arg) {
        List<T> res = new ArrayList<>();
        for (List<T> elem : arg) {
            res.addAll(elem);
        }
        return res;
    }

    private static <T> List<T> flattenIterator(Object iterable) {
        List<Object> flattened = new LinkedList<>();
        try {
            flattened.addAll(flattenIterator(asIterator(iterable)));
        } catch (IllegalArgumentException iae) {
            flattened.add(iterable);
        }
        return (List<T>) flattened;
    }

    private static List<Object> flattenIterator(Iterator iterator) {
        List<Object> flattened = new LinkedList<>();
        while (iterator.hasNext()) {
            flattened.addAll(flattenIterator(iterator.next()));
        }
        return flattened;
    }

    private static Iterator<?> asIterator(Object object) {
        if (object == null) throw new IllegalArgumentException("Null should be added");
        if (object instanceof Iterable) return ((Iterable<?>) object).iterator();
        if (object instanceof Iterator) return (Iterator<?>) object;
        if (object.getClass().isArray()) return new ResettableIteratorOnArray<>((Object[]) object);
        if (object instanceof Map) return ((Map<?, ?>) object).values().iterator();
        throw new IllegalArgumentException("Cannot convert " + object + " to an iterator");
    }

    /**
     * удаляет namespace у группировки/метрики
     *
     * @param attribute - группировка/метрика - ym:s:xxx, ym:pv:xxx
     * @return xxx
     */
    public static String removeNamespace(String attribute) {
        Matcher matcher = NAME_WITHOUT_NS_REGEX.matcher(attribute);
        return matcher.matches() ? matcher.group(1) : attribute;
    }

    /**
     * Извлекает значение измерения (группировки) в виде строки, null не преобразуется,
     * сложные/комплексные значения преобразуются в строку объединением элементов.
     *
     * @param from значение измерения (группировки)
     * @return строковое представление
     */
    public static String extractStringDimensionValue(Map<String, ?> from) {
        Object value = extractDimensionValue(from);

        if (value instanceof Iterable) {
            StringBuilder stringBuilder = new StringBuilder();
            for (Object item : ((Iterable) value)) {
                if (item instanceof Map) {
                    /* Выход из цикла сделан для того, чтобы значения измерений (группировок) не склеивались.
                       Например:
                       Ответ содержит id'шники целей. Пусть будут id: 1, 2, 3, 4, 5. Если не выходить из цикла,
                       то вернется строка 12345 и тест будет провален, ибо такой цели нет. Для тестов же нам
                       будет достаточно только первого элемента. */
                    stringBuilder.append(extractDimensionValue((Map<String, Object>) item));
                    break;
                } else {
                    stringBuilder.append(Objects.toString(item, StringUtils.EMPTY));
                }
            }
            return stringBuilder.toString();
        } else {
            return Objects.toString(value, null);
        }
    }

    /**
     * Извлекает значения измерений (группировок) в виде строки из ответа ga
     *
     * @param row  значения измерений и метрик
     * @param size количество измерений
     * @return список измерений
     */
    public static List<String> extractStringDimensionValue(List<String> row, int size) {
        List<String> result = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            result.add(row.get(i));
        }

        return result;
    }

    /**
     * Извлекает значения метрик в виде числа из ответа ga
     * Значения метрик в ответе следуют сразу же за значениями измерений
     *
     * @param row     значения измерений и метрик
     * @param dimSize количество измерений
     * @return список значений метрик
     */
    public static List<Double> extractMetricValue(List<String> row, int dimSize) {
        List<Double> result = new ArrayList<>();
        for (int i = dimSize; i < row.size(); i++) {
            result.add(Double.valueOf(row.get(i)));
        }

        return result;
    }

    /**
     * Проводит парсинг значения свойства в список пар ключ-значение
     *
     * @param rawProperty строковое свойство
     * @return список разобранных пар ключ-значение
     */
    public static List<NameValuePair> parseNameValueListProperty(String rawProperty) {
        return Stream.of(rawProperty.split(","))
                .map(StringUtils::trimToEmpty)
                .filter(s -> !isBlank(s))
                .map(s -> s.split("=", 2))
                .filter(a -> a.length == 2)
                .filter(a -> !isBlank(a[0]))
                .map(a -> new BasicNameValuePair(a[0], a[1]))
                .collect(toList());
    }

    public static String replaceParameters(String nameWithPlaceholders, IFormParameters... parameters) {
        checkNotNull(parameters);
        String result = nameWithPlaceholders;
        Map<String, String> parametersMap = Arrays.stream(parameters)
                .flatMap(p -> p.getParameters().stream())
                .collect(toMap(NameValuePair::getName, NameValuePair::getValue));
        for (ParametrizationTypeEnum p : ParametrizationTypeEnum.values()) {
            if (result.contains(p.getPlaceholder()) && parametersMap.containsKey(p.getParameterName())) {
                result = result.replace(p.getPlaceholder(), parametersMap.get(p.getParameterName()));
            }
        }
        return result;
    }

    public static <T> List<T> getSlice(Iterable<List<T>> array, int index) {
        List<T> slice = new ArrayList<>();

        for (List<T> row : array) {
            slice.add(row.get(index));
        }

        return slice;
    }

    public static URL toUrl(String url) {
        try {
            return new URL(url);
        } catch (MalformedURLException e) {
            throw propagate(e);
        }
    }

    public static boolean isOnAero() {
        return System.getProperty("aero.pack.uuid") != null &&
                System.getProperty("aero.suite.uuid") != null &&
                System.getProperty("aero.suite.name") != null;
    }

    public static String invertCase(String value) {
        StringBuilder sb = new StringBuilder();
        for (char c : value.toCharArray()) {
            String s = String.valueOf(c);
            boolean isLowerCase = s.toLowerCase().equals(s);
            sb.append(isLowerCase ? s.toUpperCase() : s.toLowerCase());
        }
        return sb.toString();
    }
}

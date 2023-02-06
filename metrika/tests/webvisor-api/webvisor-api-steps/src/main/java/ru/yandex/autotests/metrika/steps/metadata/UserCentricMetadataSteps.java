package ru.yandex.autotests.metrika.steps.metadata;

import ru.yandex.autotests.metrika.beans.CustomTree;
import ru.yandex.autotests.metrika.beans.StatV1MetadataUserAndCommonSegmentsGETSchemaCopy;
import ru.yandex.autotests.metrika.core.response.MetrikaJsonResponse;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.metrika.segments.core.meta.segment.ApiSegmentMetadata;
import ru.yandex.metrika.segments.core.meta.segment.UserFilterType;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.filters.Relation.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.UserCentricMetadataSteps.Predicates.knownFilter;
import static ru.yandex.autotests.metrika.steps.metadata.UserCentricMetadataSteps.Predicates.userAttribute;

/**
 * Created by konkov on 12.11.2015.
 */
public class UserCentricMetadataSteps extends MetrikaBaseSteps {

    private static final String USER_CENTRIC_AND_COMMON_ATTRIBUTES_PATH = "/stat/v1/metadata/user_and_common_segments";


    private static final Pattern NS_REGEX = Pattern.compile("(ym:(?:u|s|pv|dl|el|pv|sp|sh|up):).*");
    private static final String USER_ID_REPLACEMENT = "userID";
    private static final String SPECIAL_DEFAULT_DATE_REPLACEMENT = "specialDefaultDate";

    private static final String START_SPECIAL_DATE = "2017-08-31";
    private static final String END_SPECIAL_DATE = "2017-09-05";



    @Step("Получить из дерева user-centric список атрибутов типа {0}")
    public List<String> getUserCentricAttributes(UserFilterType filterType) {

        List<ApiSegmentMetadata> attributes = this.<MetrikaJsonResponse>getResponse(USER_CENTRIC_AND_COMMON_ATTRIBUTES_PATH)
                .readResponse(StatV1MetadataUserAndCommonSegmentsGETSchemaCopy.class)
                .getUsercentricSegments()
                .stream()
                .map(CustomTree::flattened)
                .flatMap(List::stream)
                .collect(toList())
                .stream()
                .filter(o -> o.getWvDim() != null)
                .collect(Collectors.toList());

        List<String> attributesWithoutFilterType = attributes
                .stream()
                .filter(a -> a.getFilterType() == null)
                .map(ApiSegmentMetadata::getWvDim)
                .collect(toList());

        assumeThat("для каждого атрибута задан filter_type",
                attributesWithoutFilterType,
                empty());

        return attributes
                .stream()
                .filter(a -> a.getFilterType().equals(filterType))
                .map(ApiSegmentMetadata::getWvDim)
                .collect(toList());
    }

    @Step ("Получить список фильтров для атрибутов типа {0} и статических фильтров {1}")
    public List<Expression> getFilters(UserFilterType filterType, Map<String, Expression> filters) {
        //1. для каждого (a) берем фильтр из статического списка сформированных фильтров.
        //2. проверяем, что для него есть фильтр, иначе фейлим тест для которого не нашли фильтра, что бы при
        //появлении новых атрибутов это быстро выявить.
        //3. комбинируем для кванторов EXISTS, ALL, NONE

        List<String> attributes = getUserCentricAttributes(filterType);
        List<String> absentItems = attributes.stream()
                .filter(a -> !filters.containsKey(a))
                .collect(toList());

        AllureUtils.assumeThat("для каждого (a) сформирован фильтр", absentItems, empty());

        return attributes.stream()
                .filter(filters::containsKey)
                .flatMap(a -> getUserCentricFilters(a, filters).stream())
                .collect(toList());
    }

    protected Collection<Expression> getUserCentricFilters(String attribute,
                                                           Map<String, Expression> expressions) {
        String userId = getUserIdAttribute(attribute);
        String specialDefaultDate = getSpecialDefaultDateAttribute(attribute);
        return asList(
                exists(userId, expressions.get(attribute)
                        .and(dimension(specialDefaultDate).greaterThan(START_SPECIAL_DATE))
                        .and(dimension(specialDefaultDate).lessThan(END_SPECIAL_DATE))),
                all(userId, expressions.get(attribute)
                        .and(dimension(specialDefaultDate).greaterThan(START_SPECIAL_DATE))
                        .and(dimension(specialDefaultDate).lessThan(END_SPECIAL_DATE))),
                none(userId, expressions.get(attribute)
                        .and(dimension(specialDefaultDate).greaterThan(START_SPECIAL_DATE))
                        .and(dimension(specialDefaultDate).lessThan(END_SPECIAL_DATE))));
    }

    @Step("Получить атрибуты, удовлетворяющие предикату")
    public Collection<String> getUserCentricAttributes(Predicate<String> predicate) {
        return getUserCentricAttributesRaw(userAttribute(predicate));
    }

    @Step("Получить атрбуты, удовлетворяющие предикату")
    public Collection<String> getUserCentricAttributesRaw(Predicate<ApiSegmentMetadata> predicate) {
        return getUserCentricAttributesMeta(predicate)
                .stream()
                .map(ApiSegmentMetadata::getWvDim)
                .collect(toList());
    }

    @Step("Получить метаданные группировок, удовлетворяющих предикату")
    public Collection<ApiSegmentMetadata> getUserCentricAttributesMeta(Predicate<ApiSegmentMetadata> predicate) {
        return getResponse(USER_CENTRIC_AND_COMMON_ATTRIBUTES_PATH)
                .readResponse(StatV1MetadataUserAndCommonSegmentsGETSchemaCopy.class)
                .getUsercentricSegments()
                .stream()
                .map(CustomTree::flattened)
                .flatMap(List::stream)
                .collect(toList())
                .stream()
                .filter(o -> o.getWvDim() != null)
                .filter(userAttribute(knownFilter()).and(predicate))
                .collect(toList());
    }

    @Step("Получить атрибут userID для атрибута {0}")
    public String getUserIdAttribute(String attributeName) {
        Matcher matcher = NS_REGEX.matcher(attributeName);
        return matcher.matches() ? matcher.group(1) + USER_ID_REPLACEMENT : null;
    }

    @Step("Получить атрибут specialDefaultDate для атрибута {0}")
    public String getSpecialDefaultDateAttribute(String attributeName) {
        Matcher matcher = NS_REGEX.matcher(attributeName);
        return matcher.matches() ? matcher.group(1) + SPECIAL_DEFAULT_DATE_REPLACEMENT : null;
    }

    public static class Predicates {

        /**
         * @return предикат - "любой", над любым типом
         */
        public static <T> Predicate<T> any() {
            return m -> true;
        }

        /**
         * @param filterType тип фильтра
         * @return предикат принадлежности атрибута указанному типу фильтра
         */
        public static Predicate<String> filterType(UserFilterType filterType) {
            return s -> s.startsWith(filterType.value());
        }

        /**
         * @return предикат принадлежности атрибута известному типу фильтра
         */
        public static Predicate<String> knownFilter() {
            return s -> Arrays.stream(UserFilterType.values()).anyMatch(t -> s.startsWith(t.toString()));
        }

        /**
         * @param predicate предикат над типом фильтра
         * @return предикат над метаданными атрибута, делегирующий вычисление предикату над типом фильтра атрибута
         */
        public static Predicate<ApiSegmentMetadata> userAttribute(Predicate<String> predicate) {
            return m -> predicate.test(m.getFilterType().toString());
        }
    }
}

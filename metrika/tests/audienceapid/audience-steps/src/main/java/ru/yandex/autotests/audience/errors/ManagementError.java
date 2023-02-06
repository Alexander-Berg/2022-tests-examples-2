package ru.yandex.autotests.audience.errors;

import org.hamcrest.Matcher;

import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.metrika.commons.response.CustomError;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.either;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.audience.data.users.User.LOGIN;

/**
 * Created by ava1on on 21.04.17.
 */
public enum ManagementError implements IExpectedError{

    LOOKALIKE_FOR_GEO_LAST(400L, equalTo("It's impossible to create dependent segment for 'last' geo segment")),
    LOOKALIKE_FOR_DMP(400L, equalTo("It's impossible to create dependent segment for dmp segment")),
    LOOKALIKE_NOT_OWNER_FOR_SOURCE(400L, both(startsWith("You must be owner of segment")).and(endsWith("to use it as source for creation of new segment"))),
    LOOKALIKE_NOT_PROCESSED_SOURCE(400L, both(startsWith("Source segment")).and(endsWith("must be processed but is not"))),
    TOO_BIG_LOOKALIKE_VALUE(400L, equalTo("должно быть меньше или равно 5")),
    TOO_SMALL_LOOKALIKE_VALUE(400L, equalTo("должно быть больше или равно 1")),
    INCORRECT_SEGMENT_NAME_LENGTH(400L, equalTo("длина должна быть между 1 и 250")),
    CRM_HEADER_VALIDATION_ERROR(400L, equalTo("Ошибка валидации заголовка в файле CRM сегмента")),
    INVALID_DATA_FORMAT(400L, startsWith("Некорректный формат данных в строке")),
    HAS_DEPENDENT_SEGMENTS(400L, startsWith("Can't remove segment because it has dependent segments:")),
    NO_ACCESS_TO_CREATE_LOOKALIKE(403L, startsWith("You must have edit grants for")),
    NOT_NULL(400L, equalTo("должно быть задано")),
    INCORRECT_NUMBER_OF_POLYGONS(400L, equalTo("размер должен быть между 1 и 10")),
    POLYGON_WITH_INTERSECTIONS(400L, equalTo("Полигон имеет самопересечения")),
    POLYGONS_ARE_ABSENT(400L, equalTo("должно быть задано")),
    POLYGON_POINTS_ARE_ABSENT(400L, equalTo("должно быть задано")),
    POLYGON_POINTS_EMPTY(400L, equalTo("size must be greater than or equal to 4")),
    RADIUS_IS_ABSENT(400L, equalTo("It's impossible to create geo segment without radius")),
    TOO_SMALL_RADIUS(400L, equalTo("It's impossible to create geo segment with radius that is less than 500")),
    TOO_BIG_RADIUS(400L, equalTo("It's impossible to create geo segment with radius that is greater than 10000")),
    PERIOD_LENGTH_IS_ABSENT(400L, equalTo("It's impossible to create condition geo segment without period length")),
    INCORRECT_PERIOD_LENGTH(400L, equalTo("It's impossible to create condition geo segment with period length that is nonpositive")),
    TOO_BIG_PERIOD_LENGTH(400L, equalTo("It's impossible to create condition geo segment with period length that is greater than 90")),
    TIME_QUANTITY_IS_ABSENT(400L, equalTo("It's impossible to create condition geo segment without times quantity")),
    QUANTITY_GREATER_PERIOD(400L, equalTo("It's impossible to create condition geo segment with times quantity that is greater than period length")),
    POINTS_ARE_ABSENT(400L, equalTo("It's impossible to create geo segment without points")),
    INCORRECT_POINT(400L, both(startsWith("Point number")).and(endsWith("is invalid"))),
    INCORRECT_LATITUDE(400L, both(startsWith("Point number")).and(endsWith("has no latitude"))),
    INCORRECT_LONGITUDE(400L, both(startsWith("Point number")).and(endsWith("has no longitude"))),
    POLYGON_WITH_LAST_COORDINATES(400L, equalTo("It's impossible to create polygon geo segment with type that is equal to last")),
    GEO_TYPE_IS_ABSENT(400L, equalTo("It's impossible to create geo segment without type")),
    TOO_MUCH_POINTS_CONDITION(400L, equalTo("It's impossible to create condition geo segment with points quantity that is greater than 100")),
    INCORRECT_STRING_LENGTH(400L, startsWith("длина должна быть между ")),
    PIXEL_HAS_DEPENDENT_SEGMENTS(400L, startsWith("Can't remove pixel because it has dependent segments:")),
    TOO_MUCH_POINTS(400L, equalTo("It's impossible to create geo segment with points quantity that is greater than 1000")),
    TOO_SMALL_PERIOD_LENGTH_PIXEL(400L, equalTo("должно быть больше или равно 1")),
    TOO_BIG_PERIOD_LENGTH_PIXEL(400L, equalTo("должно быть меньше или равно 90")),
    INCORRECT_TIMES_QUANTITY_PIXEL(400L, equalTo("It's impossible to create pixel segment with times quantity condition with times quantity that is non positive")),
    TOO_BIG_TIMES_QUANTITY_PIXEL(400L, equalTo("It's impossible to create pixel segment with times quantity that is greater than 1000")),
    PIXEL_TIMES_QUANTITY_IS_ABSENT(400L, equalTo("It's impossible to create pixel segment with times quantity condition without times quantity")),
    NO_TIMES_QUANTITY_OPERATION(400L, equalTo("It's impossible to create pixel segment with times quantity condition without times quantity operation")),
    NO_ACCESS_TO_PIXEL(400L, equalTo("Нет объекта с указанным ID.")),
    STAT_COUNTER_IS_ABSENT(400L, equalTo("goals without counter")),
    STAT_GOAL_FROM_ANOTHER_COUNTER(400L, both(startsWith("goal")).and(containsString("is not from counter"))),
    NO_OBJECT(400L, equalTo("Нет объекта с указанным ID.")),
    ACCESS_DENIED_FOR_COUNTER(403L, startsWith("Access denied for counter")),
    ACCESS_DENIED_FOR_API_KEY(403L, startsWith("Access denied for some api keys from")),
    MORE_THAN_3_GOALS(400L, equalTo("размер должен быть между 0 и 3")),
    INCORRECT_DMP_SEGMENT(400L, startsWith("It's impossible to create dmp segment with id that is")),
    CLIENT_INVALID_SEGMENT(400L, equalTo("segment_id")),
    USER_NOT_FOUND(400L, either(equalTo("User not found")).or(equalTo("Такой пользователь не существует."))),
    UPLOADING_LESS_UNIQUE_ELEMENTS(400L, either(equalTo("Количество корректных уникальных элементов меньше, чем 5")).or(equalTo("Number of correct unique elements is less than 5"))),
    MODIFY_PROCESSING_SEGMENT(400L, equalTo("It is possible to modify data of processed segments only")),
    NO_NEW_DATA_MODIFICATION(400L, equalTo("Данные сегмента не изменились")),
    WRONG_CONTENT_TYPE(400L, equalTo("Нет ни одного корректного элемента")),
    MODIFICATION_TYPE_IS_ABSENT(400L, equalTo("Required request parameter 'modification_type' is not present")),
    NO_GRANT_FOR_DMP(400L, equalTo("Нельзя выдать доступ к сегменту dmp.")),
    GRANT_HAS_ALREADY_CREATED(400L, equalTo("Разрешение этому пользователю уже выдано.")),
    ACCESS_DENIED(403L, equalTo("Access is denied")),
    LOGIN_NOT_NULL(400L, equalTo("Логин не должен быть пустым")),
    NOT_EMPTY(400L, equalTo("не может быть пусто")),
    REPROCESS_QUOTA_EXCEEDED(429L, equalTo("reprocess quota by segment exceeded")),
    REPROCESS_WRONG_TYPE(400L, containsString("can not be reprocessed")),
    EXPERIMENT_SEGMENTS_NOT_EMPTY(400L,startsWith("Количество сегментов должно быть больше нуля")),
    EXPERIMENT_TOO_FEW_SEGMENTS(400L,startsWith("too few segments")),
    EXPERIMENT_INCORRECT_SEGMENTS_COUNT(400L,startsWith("wrong segments number")),
    EXPERIMENT_TOO_FEW_COUNTERS(400L,startsWith("empty counters list")),
    EXPERIMENT_EMPTY_SEGMENT(400L,startsWith("empty segment")),
    EXPERIMENT_TOO_MANY_COUNTERS(400L,startsWith("too many counters")),
    EXPERIMENT_WRONG_SEGMENT_BOUNDARIES(400L,startsWith("wrong start/end value")),
    SEGMENT_IS_DELETED(400L,equalTo("Segment is deleted")),
    ERROR_400(400L, allOf());


    public static IExpectedError OFFER_NOT_ACCEPTED(User user){
        return new CustomError(400L, equalTo(user.get(LOGIN)));
    }

    private final Long code;
    private final Matcher<String> message;

    ManagementError(Long code, Matcher<String> message) {
        this.code = code;
        this.message = message;
    }

    public Long getCode() {
        return code;
    }

    public Matcher<String> getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return String.format("%s %s", code, message);
    }
}

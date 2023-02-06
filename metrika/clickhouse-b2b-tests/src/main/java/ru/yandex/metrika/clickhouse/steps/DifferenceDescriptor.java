package ru.yandex.metrika.clickhouse.steps;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import ru.yandex.autotests.irt.testutils.beandiffer2.Diff;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanField;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.CompareStrategy;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.autotests.irt.testutils.beandiffer2.differ.AbstractDiffer;
import ru.yandex.autotests.irt.testutils.beandiffer2.differ.Differ;
import ru.yandex.autotests.irt.testutils.beandiffer2.reporter.Reporter;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;

public class DifferenceDescriptor {
    private final String dataField;
    private final ResponseDescriptor fromTest;
    private final ResponseDescriptor fromRef;
    private ResultKind resultKind;
    private Exception internalError;
    private String consoleDiff;
    private String htmlDiff;

    private static final Gson GSON = new GsonBuilder().setLenient().create();

    private static final String[] CH_SETTINGS_ERRORS = {
            "ClickhouseQuerySizeException", "ClickhouseQueryMemoryException", "ClickhouseQueryTimeException"
    };

    /**
     * Варианты исходов.
     *
     * Если isConclusive == true, то данный исход влияет на общий результат, если false - то не влияет.
     *
     */
    public enum ResultKind {
        /**
         * Оба ответили 200, отличий нет.
         * Не ухудшает результат.
         */
        POSITIVE("отличий не обнаружено", true),
        /**
         * Оба ответили 200, отличия есть.
         * Ухудшает результат до fail.
         */
        NEGATIVE("отличия в данных", true),
        /**
         * Оба ответили разными кодами.
         * Ухудшает результат до fail.
         * C каждым таким случаем надо разбираться отдельно.
         *
         * Пример - один ответил 200, другой пятисотнул.
         * Вероятно этот случай нужно выделить вообще отдельно.
         * Или разбить их по подгруппам, ключ - пара кодов ответов.
         * Что бы в агрегированном отчёте было видно.
         */
        NOT_SIMILAR("отличие в коде ответа", true),
        /**
         * Оба ответили 200, в обоих нет данных
         */
        NO_DATA("нет данных для сравнения"),
        /**
         * Оба ответили одниковым кодом.
         * Код ответа более или равен 300 и менее 400.
         * Ухудшает до broken, а может быть и нет
         */
        UNEXPECTED("неожиданный код ответа", true),
        /**
         * Оба ответили одинаковым кодом.
         * Код ответа более или равен 400 и менее 500.
         * Не ухудшает результат, т.к. состояние mtacs в общем случае не соответствует тому, которое было
         * когда выполнялся тот или иной запрос.
         */
        BAD_REQUEST("плохой запрос"),
        /**
         * Оба ответили одинаковым кодом.
         * Код ответа равен 403 или 404
         */
        ALMOST_BAD_REQUEST("не очень плохой запрос"),
        /**
         * Оба ответили одинаковым кодом.
         * Код ответа более или равен 500
         */
        BROKEN("сломано", true),
        /**
         * Всякая проблема, с парсингом или логическая ошибка.
         * Ухудшает до broken, нужно разбираться.
         */
        INTERNAL_TEST_ERROR("внутренняя ошибка", true),
        /**
         * Всякая проблема с запросами.
         * Ухудшает до broken, нужно разбираться
         */
        EXTERNAL_TEST_ERROR("внешняя ошибка", true)
        ;


        private final String description;
        private boolean isConclusive;

        ResultKind(String description) {
            this(description, false);

        }

        ResultKind(String description, boolean isConclusive) {
            this.description = description;
            this.isConclusive = isConclusive;
        }

        public boolean isConclusive() {
            return isConclusive;
        }


        @Override
        public String toString() {
            return description;
        }
    }

    public DifferenceDescriptor(String dataField, ResponseDescriptor fromTest, ResponseDescriptor fromRef) {
        this.dataField = dataField;
        this.fromTest = fromTest;
        this.fromRef = fromRef;
        init();
    }

    private void init() {
        /*
        1. проверка кодов ответов
            1.1. Совпадают
                1.1.1 200, проверить есть ли данные, для этого нужно распарсить
                    1.1.1.1 данные есть - BeanDiffer - POSITIVE/NEGATIVE
                    1.1.1.2 данных нет - NO_DATA
                1.1.2 300<=code<400 - UNEXPECTED
                1.1.3 403, 404 - ALMOST_BAD_REQUEST
                1.1.4 400<=code<500 - BAD_REQUEST
                1.1.5 500<=code<600 - BROKEN
            1.2 Отличаются - NOT_SIMILAR
         */
        if (fromRef.getException() != null || fromTest.getException() != null) {
            resultKind = ResultKind.EXTERNAL_TEST_ERROR;
        } else {
            try {
                if (
                    Arrays.stream(CH_SETTINGS_ERRORS).anyMatch(err -> fromTest.getResponse().contains(err)) ||
                    Arrays.stream(CH_SETTINGS_ERRORS).anyMatch(err -> fromRef.getResponse().contains(err))
                ) {
                    resultKind = ResultKind.ALMOST_BAD_REQUEST;
                } else if (fromRef.getCode() == fromTest.getCode()) {
                    if (fromTest.getCode() == 200) {
                        resultKind = processResponseContent();
                    } else if (300 <= fromTest.getCode() && fromTest.getCode() < 400) {
                        resultKind = ResultKind.UNEXPECTED;
                    } else if (fromTest.getCode() == 403 || fromTest.getCode() == 404) {
                        resultKind = ResultKind.ALMOST_BAD_REQUEST;
                    } else if (400 <= fromTest.getCode() && fromTest.getCode() < 500) {
                        resultKind = ResultKind.BAD_REQUEST;
                    } else if (500 <= fromTest.getCode() && fromTest.getCode() < 600) {
                        resultKind = ResultKind.BROKEN;
                    }
                } else {
                    resultKind = ResultKind.NOT_SIMILAR;
                }
            } catch (Exception e) {
                internalError = e;
                resultKind = ResultKind.INTERNAL_TEST_ERROR;
            }
        }
    }

    private static class FloatDiffer extends AbstractDiffer {
        public FloatDiffer(BeanField field, CompareStrategy compareStrategy) {
            super(field, compareStrategy);
        }

        public FloatDiffer() {
        }

        @Override
        public List<Diff> compare(Object actual, Object expected) {
            List<Diff> result = new ArrayList<>();
            if (Math.abs((double) actual - (double) expected) > 1E-4) {
                result.add(Diff.changed(getField(), actual, expected));
            }
            return result;
        }
    }

    private static class StringDiffer extends AbstractDiffer {
        public StringDiffer(BeanField field, CompareStrategy compareStrategy) {
            super(field, compareStrategy);
        }

        public StringDiffer() {
        }

        @Override
        public List<Diff> compare(Object actual, Object expected) {
            List<Diff> result = new ArrayList<>();
            String actual_str = String.valueOf(actual);
            String expected_str = String.valueOf(expected);
            String[][] replaces = {
                    {"www.yandex.ru", "m.yandex.ru"},
                    {"yandex.ru/search/", "yandex.ru/yandsearch"},
            };
            boolean equals = expected_str.equals(actual_str);
            for (int i = 0; i < replaces.length; ++i) {
                if (equals) {
                    break;
                }
                equals |= expected_str.equals(actual_str.replace(replaces[i][0], replaces[i][1]));
                equals |= expected_str.equals(actual_str.replace(replaces[i][1], replaces[i][0]));
            }

            if (!equals) {
                result.add(Diff.changed(getField(), actual, expected));
            }
            return result;
        }
    }

    private ResultKind processResponseContent() {
        /**
         * 1. Парсим оба ответа
         * 2. проверяем есть ли данные
         * 3. применяем BeanDiffer
         */

        Map<String, Object> refParsed = GSON.fromJson(fromRef.getResponse(), new TypeToken<Map<String, Object>>(){}.getType());
        Map<String, Object> testParsed = GSON.fromJson(fromTest.getResponse(), new TypeToken<Map<String, Object>>(){}.getType());

        if (hasData(refParsed) && hasData(testParsed)) {

            Object refData = refParsed.get(dataField);
            Object testData = testParsed.get(dataField);
            Class<? extends Object> type = testData.getClass();

            DefaultCompareStrategy compareStrategy = DefaultCompareStrategies.allFields();
            compareStrategy.forClasses(Float.class,  Double.class).useDiffer(new DifferenceDescriptor.FloatDiffer());
            compareStrategy.forClasses(String.class).useDiffer(new DifferenceDescriptor.StringDiffer());
            Differ differ = compareStrategy.getCustomOrDefaultDiffer(new BeanField(BeanFieldPath.newPath(), type));
            List<Diff> diffs = differ.compare(testData, refData);
            if (diffs.isEmpty()) {
                return ResultKind.POSITIVE;
            } else {
                Reporter reporter = new Reporter(diffs, testData, refData);
                consoleDiff = reporter.attachConsoleReport();
                htmlDiff = reporter.attachJsonDiffPatch();
                return ResultKind.NEGATIVE;
            }
        } else {
            return ResultKind.NO_DATA;
        }
    }

    private boolean hasData(Map<String, Object> parsedResponse) {
        Object data = parsedResponse.getOrDefault(dataField, null);
        if (data == null) {
            return false;
        } else if(data instanceof Collection) {
            return !((Collection) data).isEmpty();
        } else if(data instanceof Map) {
            return !((Map) data).isEmpty();
        } else {
            throw new RuntimeException(String.format("Unsupported type of data field: %s", data.getClass().toString()));
        }
    }

    public boolean isHasInternalError() {
        return resultKind == ResultKind.INTERNAL_TEST_ERROR;
    }

    public boolean isHasExternalError() {
        return resultKind == ResultKind.EXTERNAL_TEST_ERROR;
    }

    public boolean isHasDiff() {
        return resultKind == ResultKind.NEGATIVE;
    }

    public ResponseDescriptor getFromTest() {
        return fromTest;
    }

    public ResponseDescriptor getFromRef() {
        return fromRef;
    }

    public ResultKind getResultKind() {
        return resultKind;
    }

    public Exception getInternalError() {
        return internalError;
    }

    public String getExternalError() {
        return String.format("Test: %s\nRef: %s", fromTest.getException(), fromRef.getException());
    }

    public String getConsoleDiff() {
        return consoleDiff;
    }

    public String getHtmlDiff() {
        return htmlDiff;
    }
}

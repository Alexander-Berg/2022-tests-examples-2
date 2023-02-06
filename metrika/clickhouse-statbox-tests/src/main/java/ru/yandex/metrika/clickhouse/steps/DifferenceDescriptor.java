package ru.yandex.metrika.clickhouse.steps;

import com.github.difflib.DiffUtils;
import com.github.difflib.algorithm.DiffException;
import com.github.difflib.patch.Patch;
import com.github.difflib.text.DiffRow;
import com.github.difflib.text.DiffRowGenerator;
import com.google.common.collect.ImmutableMap;
import freemarker.ext.beans.BeansWrapper;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import ru.yandex.metrika.clickhouse.properties.ClickhouseStatBoxB2BTestsProperties;

import java.io.IOException;
import java.io.StringWriter;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.BiPredicate;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;

public class DifferenceDescriptor {
    private final ResponseDescriptor fromTest;
    private final ResponseDescriptor fromRef;
    private ResultKind resultKind;
    private Exception internalError;
    private String consoleDiff;
    private String htmlDiff;

    public DifferenceDescriptor(ResponseDescriptor fromTest, ResponseDescriptor fromRef) {
        this.fromTest = fromTest;
        this.fromRef = fromRef;
        init();
    }

    public enum ResultKind {
        /**
         * Оба ответили 200, отличий нет.
         * Success
         */
        POSITIVE("отличий не обнаружено"),
        /**
         * Оба ответили 200, отличия есть.
         * Fail
         */
        NEGATIVE("отличия в данных"),
        /**
         * Оба ответили разными кодами.
         * Fail
         * <p>
         * Пример - один ответил 200, другой пятисотнул.
         * Вероятно этот случай нужно выделить вообще отдельно.
         * Или разбить их по подгруппам, ключ - пара кодов ответов.
         * Что бы в агрегированном отчёте было видно.
         */
        NOT_SIMILAR("отличие в коде ответа"),
        /**
         * Прочее
         * Broken
         */
        BROKEN("сломано"),
        /**
         * Всякая проблема, с парсингом или логическая ошибка.
         * Broken
         */
        INTERNAL_TEST_ERROR("внутренняя ошибка"),
        /**
         * Всякая проблема с запросами.
         * Broken
         */
        EXTERNAL_TEST_ERROR("внешняя ошибка");

        private final String description;

        ResultKind(String description) {
            this.description = description;
        }

        @Override
        public String toString() {
            return description;
        }
    }

    private class DiffPredicate implements BiPredicate<String, String> {

        private final double maxDiff;

        public DiffPredicate(double maxDiff) {
            this.maxDiff = maxDiff;
        }

        @Override
        public boolean test(String s1, String s2) {
            if (Objects.equals(s1, s2)) {
                return true;
            } else {
                return splitEquals(s1, s2);
            }
        }

        private boolean splitEquals(String s1, String s2) {
            String[] split1 = s1.split("\t");
            String[] split2 = s2.split("\t");
            if (split1.length != split2.length) {
                return false;
            }

            for (int indx = 0; indx < split1.length; indx++) {
                Pair<Boolean, Double> p1 = tryParse(split1[indx]);
                Pair<Boolean, Double> p2 = tryParse(split2[indx]);
                if (!p1.getLeft() || !p2.getLeft()) {
                    return Objects.equals(split1[indx], split2[indx]);
                } else {
                    return Math.abs(p1.getRight() - p2.getRight()) <= maxDiff;
                }
            }

            return true;
        }

        private Pair<Boolean, Double> tryParse(String s) {
            boolean result = true;
            double value = 0;
            try {
                value = Double.valueOf(s);
            } catch (NumberFormatException | NullPointerException e) {
                result = false;
            }
            return ImmutablePair.of(result, value);
        }
    }

    private void init() {
        /*
        1. проверка кодов ответов
            1.1. Совпадают
                1.1.1 200, сравнить тела ответов POSITIVE/NEGATIVE
                1.1.2 не 200 - NOT_SIMILAR
            1.2 Отличаются - NOT_SIMILAR
         */

        if (fromRef.getException() != null || fromRef.getException() != null) {
            resultKind = ResultKind.EXTERNAL_TEST_ERROR;
        } else {
            try {
                if (fromRef.getCode() == fromTest.getCode()) {
                    if (fromTest.getCode() == 200) {
                        resultKind = processResponseContent();
                    } else {
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

    private ResultKind processResponseContent() throws DiffException, IOException, TemplateException {
        /**
         * 1. Ответы сплитим на отдельные строки
         * 2. делаем дифф
         * 3. рендерим отчёты по отличиям
         * 4. выставляем соответствюущий результат
         */

        ResultKind resultKind;

        List<String> ref = asList(fromRef.getResponse().split("\n"));
        List<String> test = asList(fromTest.getResponse().split("\n"));
        Patch<String> diff = DiffUtils.diff(ref, test,
                ClickhouseStatBoxB2BTestsProperties.getInstance().isTolerance() ?
                        new DiffPredicate(ClickhouseStatBoxB2BTestsProperties.getInstance().getMaxAbsDiff()) : null);

        if (diff.getDeltas().isEmpty()) {
            resultKind = ResultKind.POSITIVE;
        } else {
            resultKind = ResultKind.NEGATIVE;
            DiffRowGenerator generator = DiffRowGenerator.create()
                    .showInlineDiffs(false)
                    .build();
            List<DiffRow> diffRows = generator.generateDiffRows(ref, diff);

            consoleDiff = diffRows.stream().map(row -> row.toString()).collect(joining("\n"));

            Configuration configuration = new Configuration();
            configuration.setTemplateExceptionHandler(TemplateExceptionHandler.DEBUG_HANDLER);
            configuration.setClassForTemplateLoading(this.getClass(), "/");
            configuration.setOutputEncoding("UTF-8");
            configuration.setDefaultEncoding("UTF-8");
            Template template = configuration.getTemplate("Diff.html.ftl");
            Map<String, Object> root = ImmutableMap.<String, Object>builder()
                    .put("diff", diffRows)
                    .put("Tag", BeansWrapper.getDefaultInstance().getEnumModels().get("com.github.difflib.text.DiffRow$Tag"))
                    .build();
            StringWriter writer = new StringWriter();
            template.process(root, writer);
            htmlDiff = writer.toString();
        }

        return resultKind;
    }

    public boolean isBroken() {
        return resultKind == ResultKind.BROKEN ||
                resultKind == ResultKind.EXTERNAL_TEST_ERROR ||
                resultKind == ResultKind.INTERNAL_TEST_ERROR;
    }

    public boolean isFailedButNotNegative() {
        return resultKind == ResultKind.EXTERNAL_TEST_ERROR ||
                resultKind == ResultKind.BROKEN ||
                resultKind == ResultKind.NOT_SIMILAR ||
                resultKind == ResultKind.INTERNAL_TEST_ERROR;
    }

    public boolean isFail() {
        return resultKind == ResultKind.NEGATIVE || resultKind == ResultKind.NOT_SIMILAR;
    }

    public boolean isSuccess() {
        return resultKind == ResultKind.POSITIVE;
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

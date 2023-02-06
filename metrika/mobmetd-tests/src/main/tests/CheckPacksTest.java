import com.google.common.collect.ImmutableList;
import com.google.common.io.ByteStreams;
import org.junit.Ignore;
import org.junit.Test;
import org.reflections.Reflections;
import ru.yandex.qatools.allure.annotations.Title;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Этот тест проверяет, что тест-сьюты, помеченные {@link Title}:
 * - либо добавлены в паки 00.test
 * - либо заигнорированы {@link Ignore}
 */
public class CheckPacksTest {

    private static final String TEST_SUITS_PACKAGE = "ru.yandex.autotests.metrika.appmetrica.tests";

    @Test
    public void checkPacks() throws IOException {
        Collection<String> titledTestSuits = getAnnotatedTestSuits(Title.class);
        Collection<String> ignoredTestSuits = getAnnotatedTestSuits(Ignore.class);

        List<String> testpack = ImmutableList.<String>builder()
                .addAll(readAllLines("/appmetrica-management-api/mobmetd-tests/00.test"))
                .addAll(readAllLines("/appmetrica-reporting-api/mobmetd-tests/00.test"))
                .build();

        List<String> missingTestSuits = titledTestSuits.stream()
                .filter(testSuit -> !testpack.contains(testSuit))
                .filter(testSuit -> !ignoredTestSuits.contains(testSuit))
                .collect(Collectors.toList());

        if (!missingTestSuits.isEmpty()) {
            throw new IllegalStateException("Some tests are not presented in test packs:\n" + String.join("\n", missingTestSuits));
        }
    }

    private static Collection<String> getAnnotatedTestSuits(Class<?> annotation) {
        return new Reflections(TEST_SUITS_PACKAGE)
                .getStore()
                .get("TypeAnnotationsScanner")
                .get(annotation.getCanonicalName());
    }

    private static List<String> readAllLines(String resourcePath) throws IOException {
        String[] lines = new String(ByteStreams.toByteArray(CheckPacksTest.class.getResourceAsStream(resourcePath)))
                .split("\n");
        return Arrays.asList(lines);
    }

}

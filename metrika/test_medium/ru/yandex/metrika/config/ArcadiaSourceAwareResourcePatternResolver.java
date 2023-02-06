package ru.yandex.metrika.config;

import java.io.File;
import java.io.IOException;
import java.util.Objects;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import ru.yandex.devtools.test.Paths;


/**
 * Хорошо подумай, может тебе не так уж и нужно пытаться понять зачем тут этот класс и что он делает.
 * Уверен? Facepalm будут болезненный!
 * Точно?
 * Ну ладно, сам захотел. Аркадийные тесты зло, если коротко.
 *
 * 1. С одной стороны мы в метрике любим загрузить конфиги Spring не из classpath,
 * а из файловой системы в случае когда поднимается API (http сервис)
 *
 * 2. Аркадийные тесты запускаются где попало и как попало на тачках с весьма
 * стрёмным окружением и в весьма стрёмных путях
 *
 * 3. Есть возможность запустить тесты с TEST_CWD(metrika/java/api/cdp/cdp-api) в ya.make, но не тут то было!
 * Большое количество аркадийных рецептов с одной стороны рассчитывает на относительные пути для ресурсов,
 * а с другой стороны так и норовит создать в текущей директории какой-нибудь файлик. Как выяснилось вот тут
 * https://st.yandex-team.ru/DEVTOOLSSUPPORT-2307#5f10545083beff0bd8ae3023 это делать нельзя если находишься
 * в папке с сорцами, а именно это делает TEST_CWD()
 *
 * Эти 3 фактора не оставляют нам шансов и приходится делать костыли(ТМ)
 *
 *
 * ВАЖНО: Этот класс должен использоваться исключительно в тестах на страх и риск использующего, так как до
 * конца не ясно на сколько сильно он и {@link ArcadiaSourceAwareBeanDefinitionReader} меняют поведения стандартного
 * контейнера Spring
 *
 * Этот класс позволяет писать в locations у аннотаций @ImportResource и @ContextConfiguration префикс у ресурса
 * 'arcadia_source_file:'. В таком случае при запуске не в аркадийном тесте он будет себя вести как обычный 'file:',
 * но при запуске из тестов в Аркадии будет необходимо указать специальную пропертю ru.yandex.metrika.source_prefix
 * в которой находится путь до исходников. В таком случае все относительные пути будет заменены на абсолютные пути относительно
 * указанных исходников. Для того, чтобы этого заработало нужно в указанных выше аннотациях в указывать значение
 * reader = ArcadiaSourceAwareBeanDefinitionReader.class
 *
 * Важно в ya.make
 * 1. Указать property
 *      SYSTEM_PROPERTIES( ru.yandex.metrika.source_prefix path/to/some/arcadia/folder)
 * 2. Добавить DATA на эту же папку
 *      DATA(arcadia/metrika/java/api/cdp/cdp-api)
 *
 */
public class ArcadiaSourceAwareResourcePatternResolver extends PathMatchingResourcePatternResolver {

    private static final Logger log = LoggerFactory.getLogger(ArcadiaSourceAwareResourcePatternResolver.class);
    private static final String FILE_PREFIX = "file:";
    private static final String ARCADIA_SOURCE_FILE_PREFIX = "arcadia_source_file:";
    private static final String ARCADIA_SOURCE_PREFIX_PROPERTY_KEY = "ru.yandex.metrika.source_prefix";

    @Nullable
    private final String arcadiaSourcePrefix = System.getProperty(ARCADIA_SOURCE_PREFIX_PROPERTY_KEY, null);

    @Nonnull
    @Override
    public Resource[] getResources(@Nonnull String locationPattern) throws IOException {
        // честно стырено из PathMatchingResourcePatternResolver
        int prefixEnd = (locationPattern.startsWith("war:") ? locationPattern.indexOf("*/") + 1 :
                locationPattern.indexOf(':') + 1);

        var prefix = locationPattern.substring(0, prefixEnd);
        var path = locationPattern.substring(prefixEnd);
        // enemy spotted
        if (prefix.equals(ARCADIA_SOURCE_FILE_PREFIX)) {
            var originalLocationPattern = locationPattern;
            if (EnvironmentHelper.inArcadiaTest && !path.startsWith("/")) {
                Objects.requireNonNull(
                        arcadiaSourcePrefix,
                        "Specify " + ARCADIA_SOURCE_PREFIX_PROPERTY_KEY + " property for proper " +
                                "resource location resolution with '" + ARCADIA_SOURCE_FILE_PREFIX +"' prefix"
                );
                locationPattern = FILE_PREFIX + Paths.getSourcePath(arcadiaSourcePrefix + File.separator + path);
            } else {
                locationPattern = FILE_PREFIX + path;
            }
            log.info("Override location pattern. Before: {}. After: {}", originalLocationPattern, locationPattern);
        }
        return super.getResources(locationPattern);
    }


}

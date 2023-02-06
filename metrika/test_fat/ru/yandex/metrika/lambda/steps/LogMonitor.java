package ru.yandex.metrika.lambda.steps;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Map;

import io.qameta.allure.Allure;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.Appender;
import org.apache.logging.log4j.core.Filter;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.FileAppender;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.config.LoggerConfig;
import org.apache.logging.log4j.core.layout.PatternLayout;

import ru.yandex.devtools.test.Paths;

import static java.lang.String.format;


/**
 * Монитор лога log4j, добавляет свой аппендер и перенаправляет лог во временный файл.
 * По завершении работы прикрепляет лог к протоколу Allure.
 * <p>
 * Размер лога ограничен свободным местом на диске.
 * <p>
 * Таких мониторов может быть одновременно активно несколько, различаются именем,
 * которое определяет и заголовки аттачей в протоколе Allure.
 * <p>
 * Created by konkov on 19.12.2015.
 */
public class LogMonitor implements AutoCloseable {
    private static final String LOG_PATTERN = "%d{yyyy-MM-dd HH:mm:ss} %5p %t %c{1}:%M:%L - %m%n";
    private final String title;
    private final Filter filter;
    private Path logFile;
    private FileWriter logWriter;
    private FileAppender writerAppender;

    /**
     * Инициализирует мониторинг лога
     *
     * @param title - наименоваие монитора
     */
    public LogMonitor(String title) {
        this(title, null);
    }

    /**
     * Инициализирует мониторинг лога
     *
     * @param title  - наименоваие монитора
     * @param filter - фильтр сообщений лога
     */
    public LogMonitor(String title, Filter filter) {
        this.title = title;
        this.filter = filter;
        addAppender();
    }

    @Override
    public void close() {
        try {
            LoggerContext context = LoggerContext.getContext(false);
            Configuration configuration = context.getConfiguration();
            LoggerConfig loggerConfig = configuration.getLoggerConfig(LogManager.getRootLogger().getName());
            Map<String, Appender> appenders = loggerConfig.getAppenders();
            if(appenders != null) {
                appenders.remove(writerAppender.getName());
            }
            logWriter.close();
            Allure.addAttachment(title, Files.newInputStream(logFile, StandardOpenOption.READ));
        } catch (IOException e) {
            Allure.addAttachment(format("Ошибка при обработке лога %s", title), e.toString());
        }
    }

    private void addAppender() {
        try {
            final Path logMonitorDir = Path.of(Paths.getTestOutputsRoot(), "LogMonitor");
            if (!Files.exists(logMonitorDir)) {
                Files.createDirectories(logMonitorDir);
            }
            logFile = Files.createTempFile(logMonitorDir, "LogMonitor_", ".log");
            logWriter = new FileWriter(logFile.toFile());

            writerAppender = FileAppender.newBuilder()
                    .withFileName(logFile.toFile().getAbsolutePath())
                    .setName("myFilter")
                    .setFilter(filter)
                    .setLayout(PatternLayout.newBuilder().withPattern(LOG_PATTERN).build())
                    .build();

            LoggerContext context = LoggerContext.getContext(false);
            Configuration configuration = context.getConfiguration();
            LoggerConfig loggerConfig = configuration.getLoggerConfig(LogManager.getRootLogger().getName());
            loggerConfig.addAppender(writerAppender, Level.INFO, filter);
        } catch (Throwable e) {
            Allure.addAttachment(format("Ошибка при инициализации мониторинга лога %s", title), e.toString());
        }
    }
}

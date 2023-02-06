package ru.yandex.metrika.mobmet.crash.decoder.test.common;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.util.io.IOUtils;

import static java.lang.String.format;
import static ru.yandex.devtools.test.Paths.getBuildPath;

public class YdbCrashSymbolsLoader {

    private static final Logger log = LoggerFactory.getLogger(YdbCrashSymbolsLoader.class);

    public static void restoreIosFunctions() {
        log.info("Loading ios functions");
        ydbCli("tools", "restore", "-p", "ios", "-i", "ios/functions", "--upload-batch-rus", "0");
        ydbCli("tools", "restore", "-p", "ios", "-i", "ios/functions_compressed", "--upload-batch-rus", "0");
    }

    public static void restoreAndroidFunctions() {
        log.info("Loading android proguard mappings");
        ydbCli("tools", "restore", "-p", "proguard_mappings", "-i", "proguard_mappings/class_map", "--upload-batch-rus", "0");
        ydbCli("tools", "restore", "-p", "proguard_mappings", "-i", "proguard_mappings/class_map_compressed", "--upload-batch-rus", "0");
        ydbCli("tools", "restore", "-p", "proguard_mappings", "-i", "proguard_mappings/class_member_map", "--upload-batch-rus", "0");
        ydbCli("tools", "restore", "-p", "proguard_mappings", "-i", "proguard_mappings/class_member_map_compressed", "--upload-batch-rus", "0");

        log.info("Loading android r8 mappings");
        ydbCli("tools", "restore", "-p", "r8", "-i", "r8/class_map_compressed", "--upload-batch-rus", "0");
        ydbCli("tools", "restore", "-p", "r8", "-i", "r8/class_member_map_compressed", "--upload-batch-rus", "0");
    }

    public static void ydbCli(String... ydbCommand) {
        try {
            ProcessBuilder builder = new ProcessBuilder();
            List<String> command = new ArrayList<>();
            command.add(getBuildPath("kikimr/public/tools/ydb/ydb"));
            command.addAll(List.of("-e", System.getenv("YDB_ENDPOINT")));
            command.addAll(List.of("-d", "/" + System.getenv("YDB_DATABASE")));
            command.addAll(List.of(ydbCommand));
            builder.command(command);
            Process process = builder.start();
            process.waitFor();
            if (process.getInputStream() != null || process.getErrorStream() != null) {
                log.debug(format("YDB CLI\nstdout: %s\nstderr: %s",
                        IOUtils.toString(process.getInputStream()),
                        IOUtils.toString(process.getErrorStream())));
            }
        } catch (IOException exception) {
            log.error("Failed to start YDB CLI");
            throw new RuntimeException(exception);
        } catch (InterruptedException exception) {
            log.error("YDB CLI execution failed");
            throw new RuntimeException(exception);
        }
    }

}

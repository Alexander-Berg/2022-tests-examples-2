package ru.yandex.metrika.mobmet.crash.decoder.test.common;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.zip.GZIPInputStream;

import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.compress.utils.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Указанные здесь имена файлов выкачиваются в ya.make medium тестов
 */
public class SandboxDataUnpacker {

    private static final Logger log = LoggerFactory.getLogger(SandboxDataUnpacker.class);

    private static final Path TARGET_CRASHES = Paths.get("crashes");

    public static void unpack() {
        try {
            if (Files.exists(TARGET_CRASHES)) {
                return;
            }
            log.info("Unpacking sandbox data resource crashes.tar.gz into {}", TARGET_CRASHES.toAbsolutePath());
            try (TarArchiveInputStream is = new TarArchiveInputStream(new GZIPInputStream(
                    new FileInputStream("crashes.tar.gz")))) {
                copyToDir(is, TARGET_CRASHES, true);
            }
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }

    private static void copyToDir(TarArchiveInputStream is, Path targetDir, boolean skipRootFolder) throws IOException {
        TarArchiveEntry entry;
        while ((entry = is.getNextTarEntry()) != null) {
            if (!is.canReadEntryData(entry)) {
                continue;
            }
            Path entryPath = Paths.get(entry.getName());
            Path destinationPath;
            if (skipRootFolder) {
                if (entryPath.getNameCount() <= 1) {
                    continue;
                }
                destinationPath = targetDir.resolve(entryPath.subpath(1, entryPath.getNameCount()));
            } else {
                destinationPath = targetDir.resolve(entryPath);
            }

            if (Files.exists(destinationPath)) {
                continue;
            }

            if (entry.isDirectory()) {
                Files.createDirectories(destinationPath);
            } else {
                Path parentPath = destinationPath.getParent();
                if (!Files.exists(parentPath)) {
                    Files.createDirectories(parentPath);
                }
                try (OutputStream o = Files.newOutputStream(destinationPath)) {
                    IOUtils.copy(is, o);
                }
            }
        }
    }
}

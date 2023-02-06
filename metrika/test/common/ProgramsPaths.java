package ru.yandex.metrika.mobmet.crash.decoder.test.common;

import static ru.yandex.devtools.test.Paths.getBuildPath;

public class ProgramsPaths {

    public static String llvmCxxFiltPath() {
        return getBuildPath("contrib/libs/llvm12/tools/llvm-cxxfilt/llvm-cxxfilt");
    }

    public static String symbolsCutter() {
        return getBuildPath("metrika/java/tools/symbols-cutter/symbols-cutter");
    }

    /**
     * https://st.yandex-team.ru/DEVTOOLSSUPPORT-9008
     */
    public static String swiftDemanglePath() {
        return System.getenv("SWIFT_DEMANGLE_RESOURCE_GLOBAL_FULL_PATH");
    }
}

package com.yandex.launcher.lint.app

import com.android.tools.lint.checks.infrastructure.LintDetectorTest
import com.android.tools.lint.detector.api.Detector
import com.android.tools.lint.detector.api.Issue
import com.yandex.tv.common.lint.IsModuleUsageDetector

@Suppress("UnstableApiUsage")
class IsModuleUsageDetectorTest : LintDetectorTest() {

    private val BOARD_UTILS_STUB = java(
        """
        package com.yandex.tv.common.config;
        
        public class BoardUtils {

            public static boolean isModule() {
                return false;
            }
        } 
        """.trimIndent()
    )

    private val negativeFile = kotlin(
        """
        package com.yandex.tv.common.utility
        
        import android.util.Log
        import com.yandex.tv.common.device.utils.BoardUtils
        
        fun main () {
            val isModule = BoardUtils.isModule()
            println(isModule)
        }
        """.trimIndent()
    )

    fun testNegativeFile() {
        lint()
            .files(BOARD_UTILS_STUB, negativeFile)
            .allowMissingSdk()
            .run()
            .expect("""
                src/com/yandex/tv/common/utility/test.kt:7: Error: Please try to avoid using isModule() directly. Consider using DeviceSpecificResources class instead. [IsModuleUsage]
                    val isModule = BoardUtils.isModule()
                                              ~~~~~~~~
                1 errors, 0 warnings
            """.trimIndent())
    }

    override fun getDetector(): Detector {
        return IsModuleUsageDetector()
    }

    override fun getIssues(): List<Issue> {
        return listOf(IsModuleUsageDetector.ISSUE)
    }
}

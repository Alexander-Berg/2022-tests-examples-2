package com.yandex.launcher.lint.app

import com.android.tools.lint.checks.infrastructure.LintDetectorTest
import com.android.tools.lint.detector.api.Detector
import com.android.tools.lint.detector.api.Issue
import com.yandex.tv.common.lint.RemoteConfigDetector
import org.junit.Test

@Suppress("UnstableApiUsage")
class RemoteConfigDetectorTest : LintDetectorTest() {

    private val INTERFACE_ANNOTATION = kotlin(
        """
        package com.yandex.io.sdk.config

        @Retention(AnnotationRetention.SOURCE)
        annotation class RemoteConfigInterface
        
        @Retention(AnnotationRetention.SOURCE)
        annotation class RemoteConfigField(
            val path: String,
            val ticket: String,
            val default: String
        )
        """
    ).indented()

    private val INTERFACE_TEST = kotlin(
        """
        package com.yandex.io.sdk.config

        interface AConfig {
            var a: Boolean
        }

        @RemoteConfigInterface
        interface BConfig {
            @RemoteConfigField("", "", "")
            var b: Boolean
        }
        """
    ).indented()

    private val SUPER = kotlin(
        """
        package com.yandex.io.sdk.config

        @RemoteConfigClass
        abstract class ConfigsHolder(appContext: Context,
                                     private val configServiceSdk2: YandexIoConfigServiceSdk2 = YandexIoConfigServiceSdk2.Factory.create(appContext),
                                     private val configCache: SharedPreferencesHolder? = null
        )
        """
    ).indented()

    private val NEGATIVE_FILE = kotlin(
        """
        package com.yandex.io.sdk.config

        abstract class A(appContext: Context,
                                     configServiceSdk2: YandexIoConfigServiceSdk2,
                                     configCache: SharedPreferencesHolder?
        ): ConfigsHolder(appContext, configServiceSdk2, configCache), AConfig
        """
    ).indented()

    private val POSITIVE_FILE = kotlin(
        """
        package com.yandex.io.sdk.config

        @RemoteConfigClass
        abstract class B(appContext: Context,
                                     configServiceSdk2: YandexIoConfigServiceSdk2,
                                     configCache: SharedPreferencesHolder?
        ): A(appContext, configServiceSdk2, configCache), BConfig
        """
    ).indented()


    @Test
    fun testNegativeFile() {
        lint()
            .files(SUPER, INTERFACE_ANNOTATION, INTERFACE_TEST, NEGATIVE_FILE, POSITIVE_FILE)
            .allowMissingSdk()
            .run()
            .expectErrorCount(2)
    }

    override fun getDetector(): Detector {
        return RemoteConfigDetector()
    }

    override fun getIssues(): List<Issue> {
        return listOf(RemoteConfigDetector.INTERFACE_ISSUE, RemoteConfigDetector.METHOD_ISSUE)
    }
}

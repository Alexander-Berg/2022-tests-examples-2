package com.yandex.launcher.lint.app

import com.android.tools.lint.checks.infrastructure.LintDetectorTest
import com.android.tools.lint.detector.api.Detector
import com.android.tools.lint.detector.api.Issue
import com.yandex.tv.common.lint.ActionContainerIntentFilterDeclarationDetector
import org.junit.Test

@Suppress("UnstableApiUsage")
class ActionContainerIntentFilterDeclarationDetectorTest : LintDetectorTest() {

    private val MANIFEST = manifest(
        """
        <manifest xmlns:android="http://schemas.android.com/apk/res/android"
            package="com.yandex.tv.home">

            <application
                android:name=".HomeApplication"
                android:icon="@mipmap/ic_launcher"
                android:label="@string/app_name">
        
                <activity
                    android:name=".HomeActivity"
                    android:label="@string/app_name">
                    <intent-filter>
                        <action android:name="android.intent.action.MAIN" />
                        <category android:name="android.intent.category.HOME" />
                        <category android:name="android.intent.category.DEFAULT" />
                        <category android:name="android.intent.category.LAUNCHER" />
                        <category android:name="android.intent.category.LEANBACK_LAUNCHER" />
                    </intent-filter>
                    <intent-filter>
                        <action android:name="com.yandex.tv.common.ACTION_EXECUTE_CONTAINED_ACTION" />
                        <category android:name="android.intent.category.DEFAULT" />
                        <data android:scheme="action-container"
                            android:host="NAlice.NScenarios.TTvOpenDetailsScreenDirective" />
                        <data android:scheme="action-container"
                            android:host="NAlice.NScenarios.TTvOpenPersonScreenDirective" />
                        <data android:scheme="action-container"
                            android:host="NAlice.NScenarios.TTvOpenCollectionScreenDirective" />
                    </intent-filter>
                </activity>
            </application>
        </manifest>
        """
    ).indented()

    private val SUPER = kotlin(
        """
        package com.yandex.tv.common.action_containers
        
        interface IContainedActionHandler {
            fun handle(action: Any)
        
            fun canHandle(action: Any): Boolean
        
            fun handle(actions: List<Any>) {}
        
            fun canHandle(actions: List<Any>): Boolean {
                return true
            }
        }
        
        abstract class ContainedActionHandlerImpl: IContainedActionHandler {
            abstract val handledTypeName: String
        
            private val handledTypeUrl
                get() = "KEK" + handledTypeName
        
            override fun canHandle(action: Any): Boolean {
                return true
            }
        }
        """
    ).indented()

    private val NEGATIVE_FILE = kotlin(
        """
        package com.yandex.tv.home.action_containers
        
        import com.yandex.tv.common.action_containers.ContainedActionHandlerImpl
        
        class OpenActorActionHandler: ContainedActionHandlerImpl() {
            override val handledTypeName = "NAlice.NScenarios.TTvOpenPersonScreenDirective"
        
            override fun handle(action: Any) {}
        }
        """
    ).indented()

    private val POSITIVE_FILE = kotlin(
        """
        package com.yandex.tv.home.action_containers
        
        import com.yandex.tv.common.action_containers.ContainedActionHandlerImpl
        
        class OpenUnknownHandler: ContainedActionHandlerImpl() {
            override val handledTypeName = "Unknown"
        
            override fun handle(action: Any) {}
        }
        """
    ).indented()


    @Test
    fun testNegativeFile() {
        lint()
            .files(MANIFEST, SUPER, NEGATIVE_FILE)
            .allowMissingSdk()
            .run()
            .expectClean()
    }

    @Test
    fun testPositiveFile() {
        val expected =
            "src/com/yandex/tv/home/action_containers/OpenUnknownHandler.kt:6: Error: No intent filter declared for this action type [ActionContainerIntentFilterDeclaration]\n" +
                    "    override val handledTypeName = \"Unknown\"\n" +
                    "                 ~~~~~~~~~~~~~~~\n" +
                    "1 errors, 0 warnings"
        lint()
            .files(MANIFEST, SUPER, POSITIVE_FILE)
            .allowMissingSdk()
            .run()
            .expect(expected)
    }

    override fun getDetector(): Detector {
        return ActionContainerIntentFilterDeclarationDetector()
    }

    override fun getIssues(): List<Issue> {
        return listOf(ActionContainerIntentFilterDeclarationDetector.ISSUE)
    }
}

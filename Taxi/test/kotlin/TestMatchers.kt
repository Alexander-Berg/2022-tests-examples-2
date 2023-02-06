import org.junit.After
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.runners.JUnit4
import org.junit.runner.RunWith
import org.junit.Test
import ru.yandex.gradle.android._class.transform.asm.AsmDataMatcher
import ru.yandex.gradle.android._class.transform.weaver.*

@RunWith(JUnit4::class)
@Suppress("LocalVariableName")
class TestMatchers {

    // classes/packages that contains those imports should be excluded while weaving
    private val importsExclude = setOf(
            "packer",
            "protector",
            "camera",
            "speechkit",
            "yandexnavi",
            "yandexmaps",
            "tanker",
            "i18n"
    )
    private val matchingParams = ClassWeaverParams(
            includeAllClasses = false,
            matchingPath = "ru[\\%s]yandex",
            replaceWith = "ru\\%sexample",
            includeImplicitly = setOf("ru[\\.|\\/]example"),
            exclude = setOf("ru[\\%1\$s](yandex|yandextaxi)[\\%1\$s](${importsExclude.joinToString(separator = "|")})")
    )

    @After
    fun onAfterTestFinish() {
        TestLoggingDecorator.propagateLogs().forEach(::println)
    }

    @Test
    fun weaveClassMatchingTest() {
        val stubWeaver = BytecodeWeaver(TestLoggingDecorator, matchingParams)

        val shouldPass = arrayOf(
                "ru/yandex/taxi/common/rx/RxExtensionsKt\$repeatWhenSingle\$2\$1.class",
                "ru/yandex/taxi/common/rx/RxExtensionsKt.class",
                "ru/yandex/taximeter/analytics/metrica/TimelineReporter\$DefaultImpls.class",
                "ru/yandex/taximeter/clock/CombinedTimestamp.class",
                "ru/example/taximeter/ExampleApplication.class",
                "ru/example/taximeter/ExampleApplication\$1.class",
                "ru/example/taximeter/ExampleApplication\$lambda-Iwqo12343Pi1\$1\$5\$Companion.class"
        )
        val shouldNotPass = arrayOf(
                "ru/yandex/i18n/RsLocalizedPreferences.class",
                "ru/yandex/i18n/ByUrlFields.class",
                "ru/yandex/camera/api/CameraBuilder\$1.class",
                "ru/yandex/camera/api/Action.class",
                "com/yandex/metrica/impl/ob/ru.class",
                "ru/yandex/speechkit/PhraseSpotter\$Builder.class",
                "ru/yandex/speechkit/PhraseSpotter\$1.class",
                "net/dunlow/jodatime/JodaTime.class",
                "com/android/gms/AuthKey.class",
                "com/android/firebase/Firebase.class",
                "org/gradle/runner/Action.class",
                "com/okhttp/OkHttp.class",
                "ru/yandextaxi/protector/annotations/ProtectorKey.class"
        )

        (shouldPass + shouldNotPass).forEach { classPath ->
            val result = stubWeaver.isWeaveableClass(classPath)
            println("$classPath : $result")

            if (classPath in shouldPass) assertTrue(result)
            else assertFalse(result)
        }
    }

    @Test
    fun `test asm matchers should pass all`() {
        val classNameMatcher = AsmDataMatcher.ClassName(matchingParams)
        val fieldValueMatcher = AsmDataMatcher.FieldType(matchingParams)
        val inlineMethodNameMatcher = AsmDataMatcher.InlinedMethodName(matchingParams)
        val inlineFieldNameMatcher = AsmDataMatcher.InlinedFieldName(matchingParams)

        val `should pass class names` = arrayOf(
                "ru/yandex/taximeter/clock/CombinedTimestamp.class",
                "ru/yandex/taximeter/BuildConfigFacade.class"
        )

        val `should pass field types` = arrayOf(
                "ru.yandex.taximeter.clock.Timestamp",
                "ru.yandex.taximeter.data.Order",
                "ru.yandex.navibridge.yanavi.YaNaviProvider"
        )

        val `should pass inlined method names` = arrayOf(
                "ajc\$interMethod\$ru_yandex_taximeter_night_NightModeCheck\$android_support_v7_app_AppCompatActivity\$isOnCreateCalled"
        )

        val `should pass inlined field names` = arrayOf(
                "\$SwitchMap\$ru\$yandex\$taximeter\$DistributionChannel",
                "\$SWITCH_TABLE\$ru\$yandex\$taximeter\$metrika\$NavigableViewType"
        )

        assertTrue(`should pass class names`.all(classNameMatcher::matches))
        assertTrue(`should pass field types`.all(fieldValueMatcher::matches))
        assertTrue(`should pass inlined method names`.all(inlineMethodNameMatcher::matches))
        assertTrue(`should pass inlined field names`.all(inlineFieldNameMatcher::matches))
    }

    @Test
    fun `test asm matchers should replace all`() {
        val classNameMatcher = AsmDataMatcher.ClassName(matchingParams)
        val fieldValueMatcher = AsmDataMatcher.FieldType(matchingParams)
        val inlineMethodNameMatcher = AsmDataMatcher.InlinedMethodName(matchingParams)
        val inlineFieldNameMatcher = AsmDataMatcher.InlinedFieldName(matchingParams)

        val `should pass class names` = arrayOf(
                "ru/yandex/taximeter/clock/CombinedTimestamp.class",
                "ru/yandex/taximeter/BuildConfigFacade.class"
        )

        val `should pass field types` = arrayOf(
                "ru.yandex.taximeter.clock.Timestamp",
                "ru.yandex.taximeter.data.Order",
                "ru.yandex.navibridge.yanavi.YaNaviProvider"
        )

        val `should pass inlined method names` = arrayOf(
                "ajc\$interMethod\$ru_yandex_taximeter_night_NightModeCheck\$android_support_v7_app_AppCompatActivity\$isOnCreateCalled"
        )

        val `should pass inlined field names` = arrayOf(
                "\$SwitchMap\$ru\$yandex\$taximeter\$DistributionChannel",
                "\$SWITCH_TABLE\$ru\$yandex\$taximeter\$metrika\$NavigableViewType"
        )

        assertTrue(
                (`should pass class names` + `should pass field types` + `should pass inlined method names` + `should pass inlined field names`)
                        .none { str -> "example" in str }
        )

        val replaceCheckFunc = { string: String ->
            "example" in string
        }

        assertTrue(`should pass class names`.map(classNameMatcher::replace).also(::println).all(replaceCheckFunc))
        assertTrue(`should pass field types`.map(fieldValueMatcher::replace).also(::println).all(replaceCheckFunc))
        assertTrue(`should pass inlined method names`.map(inlineMethodNameMatcher::replace).also(::println).all(replaceCheckFunc))
        assertTrue(`should pass inlined field names`.map(inlineFieldNameMatcher::replace).also(::println).all(replaceCheckFunc))
    }
}
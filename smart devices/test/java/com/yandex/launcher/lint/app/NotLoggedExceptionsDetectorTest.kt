package com.yandex.launcher.lint.app

import com.android.tools.lint.checks.infrastructure.LintDetectorTest
import com.android.tools.lint.checks.infrastructure.TestFiles.kt
import com.android.tools.lint.detector.api.Detector
import com.android.tools.lint.detector.api.Issue
import com.yandex.tv.common.lint.NotLoggedExceptionsDetector
import java.io.ByteArrayInputStream
import java.io.InputStream

@Suppress("UnstableApiUsage")
class NotLoggedExceptionsDetectorTest : LintDetectorTest() {

    private val  positiveFile = "package com.yandex.tv.home.utils;\n" +
            "\n" +
            "import android.content.ContentResolver;\n" +
            "import android.content.Context;\n" +
            "import android.content.res.Resources;\n" +
            "import android.net.Uri;\n" +
            "\n" +
            "import androidx.annotation.AnyRes;\n" +
            "import androidx.annotation.NonNull;\n" +
            "import androidx.annotation.Nullable;\n" +
            "\n" +
            "public class Utils {\n" +
            "\n" +
            "    private Utils() {}\n" +
            "\n" +
            "    @Nullable\n" +
            "    public static Uri getUriToResource(@NonNull Context context, @AnyRes int resId) throws Resources.NotFoundException {\n" +
            "        try {\n" +
            "            Resources res = context.getResources();\n" +
            "            return Uri.EMPTY.buildUpon()\n" +
            "                    .scheme(ContentResolver.SCHEME_ANDROID_RESOURCE)\n" +
            "                    .authority(res.getResourcePackageName(resId))\n" +
            "                    .appendPath(res.getResourceTypeName(resId))\n" +
            "                    .appendPath(res.getResourceEntryName(resId))\n" +
            "                    .build();\n" +
            "        } catch (Resources.NotFoundException e) {\n" +
            "            Logger.e(TAG, \"error\");" +
            "            return null;\n" +
            "        }\n" +
            "    }\n" +
            "}\n"

    private val positiveIgnoredFile = "package com.yandex.tv.home.utils;\n" +
            "\n" +
            "import android.content.ContentResolver;\n" +
            "import android.content.Context;\n" +
            "import android.content.res.Resources;\n" +
            "import android.net.Uri;\n" +
            "\n" +
            "import androidx.annotation.AnyRes;\n" +
            "import androidx.annotation.NonNull;\n" +
            "import androidx.annotation.Nullable;\n" +
            "\n" +
            "public class Utils {\n" +
            "\n" +
            "    private Utils() {}\n" +
            "\n" +
            "    @Nullable\n" +
            "    public static Uri getUriToResource(@NonNull Context context, @AnyRes int resId) throws Resources.NotFoundException {\n" +
            "        try {\n" +
            "            Resources res = context.getResources();\n" +
            "            return Uri.EMPTY.buildUpon()\n" +
            "                    .scheme(ContentResolver.SCHEME_ANDROID_RESOURCE)\n" +
            "                    .authority(res.getResourcePackageName(resId))\n" +
            "                    .appendPath(res.getResourceTypeName(resId))\n" +
            "                    .appendPath(res.getResourceEntryName(resId))\n" +
            "                    .build();\n" +
            "        } catch (Resources.NotFoundException ignored) {\n" +
            "            return null;\n" +
            "        }\n" +
            "    }\n" +
            "}\n"

    private val negativeFile = "package com.yandex.tv.home.utils;\n" +
            "\n" +
            "import android.content.ContentResolver;\n" +
            "import android.content.Context;\n" +
            "import android.content.res.Resources;\n" +
            "import android.net.Uri;\n" +
            "\n" +
            "import androidx.annotation.AnyRes;\n" +
            "import androidx.annotation.NonNull;\n" +
            "import androidx.annotation.Nullable;\n" +
            "\n" +
            "public class Utils {\n" +
            "\n" +
            "    private Utils() {}\n" +
            "\n" +
            "    @Nullable\n" +
            "    public static Uri getUriToResource(@NonNull Context context, @AnyRes int resId) throws Resources.NotFoundException {\n" +
            "        try {\n" +
            "            Resources res = context.getResources();\n" +
            "            return Uri.EMPTY.buildUpon()\n" +
            "                    .scheme(ContentResolver.SCHEME_ANDROID_RESOURCE)\n" +
            "                    .authority(res.getResourcePackageName(resId))\n" +
            "                    .appendPath(res.getResourceTypeName(resId))\n" +
            "                    .appendPath(res.getResourceEntryName(resId))\n" +
            "                    .build();\n" +
            "        } catch (Resources.NotFoundException e) {\n" +
            "            return null;\n" +
            "        }\n" +
            "    }\n" +
            "}\n"

    private val negativeKt = "package com.yandex.tv.home.utils\n" +
            "import com.yandex.launcher.logger.KLogger\n" +
            "import org.json.JSONArray\n" +
            "import org.json.JSONException\n" +
            "import org.json.JSONObject\n" +
            "\n" +
            "fun safeJSONObject(jsonString: String): JSONObject? {\n" +
            "    return try {\n" +
            "        JSONObject(jsonString)\n" +
            "    } catch (e: JSONException) {\n" +
            "        null\n" +
            "    }\n" +
            "}"

    fun testPositive() {
        lint().files(
            java(positiveFile)
        ).allowMissingSdk().run().expectClean()
    }

    fun testPositiveIgnored() {
        lint().files(
            java(positiveIgnoredFile)
        ).allowMissingSdk().run().expectClean()
    }

    fun testNegative() {
        val expected = "src/com/yandex/tv/home/utils/Utils.java:26: Error: Either use Logger.e to log exception or name it ignored [YandexTvNotLoggedExceptions]\n" +
                "        } catch (Resources.NotFoundException e) {\n" +
                "          ^\n" +
                "1 errors, 0 warnings".trimIndent()
        lint().files(
            java(negativeFile),
        ).allowMissingSdk().vital(false).run().expectErrorCount(1).expect(expected)
    }

    fun testNegativeKt() {
        val expected = "src/com/yandex/tv/home/utils/test.kt:10: Error: Either use Logger.e to log exception or name it ignored [YandexTvNotLoggedExceptions]\n" +
                "    } catch (e: JSONException) {\n" +
                "      ^\n" +
                "1 errors, 0 warnings".trimIndent()
        lint().files(
            kt(negativeKt)
        ).allowMissingSdk().run().expectErrorCount(1).expect(expected)
    }

    override fun getDetector(): Detector {
        return NotLoggedExceptionsDetector()
    }

    override fun getIssues(): List<Issue> {
        return listOf(NotLoggedExceptionsDetector.ISSUE)
    }

    override fun getTestResource(relativePath: String, expectExists: Boolean): InputStream {
        return ByteArrayInputStream("".toByteArray())
    }
}

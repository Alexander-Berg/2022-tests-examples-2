package com.yandex.io.sdk.directives

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import org.junit.Test
import org.junit.runner.RunWith
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.hasToString
import org.mockito.kotlin.mock
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class SendAndroidAppIntentDirectiveHandlerTest {
    @Test
    fun `fully specified directive, createIntent, intent has all fields`() {
        val directive = SendAndroidAppIntentDirective("42", "name",
            action = "ru.yandex.tv.TEST_ACTION",
            uri = Uri.parse("vnd.youtube:dQw4w9WgXcQ"),
            category = "test.category",
            type = "test.type",
            component = SendAndroidAppIntentDirective.Component("component.package", "component.class"),
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_NO_HISTORY
        )
        val context = ApplicationProvider.getApplicationContext<Application>()
        val handler = SendAndroidAppIntentDirectiveHandler(context, mock())

        val intent = handler.createIntent(directive)

        assertThat(intent, hasToString(
            "Intent { act=ru.yandex.tv.TEST_ACTION cat=[test.category] typ=test.type flg=0x50000000 cmp=component.package/component.class }"))
    }

    @Test
    fun `uri is not null, createIntent, intent has data`() {
        val directive = SendAndroidAppIntentDirective("42", "name",
            action = "ru.yandex.tv.TEST_ACTION",
            uri = Uri.parse("vnd.youtube:dQw4w9WgXcQ")
        )
        val context = ApplicationProvider.getApplicationContext<Application>()
        val handler = SendAndroidAppIntentDirectiveHandler(context, mock())

        val intent = handler.createIntent(directive)

        assertThat(intent, hasToString(
            "Intent { act=ru.yandex.tv.TEST_ACTION dat=vnd.youtube:dQw4w9WgXcQ }"))
    }

    @Test
    fun `directive has no fields, createIntent, intent has no fields`() {
        val directive = SendAndroidAppIntentDirective("42", "name")
        val context = ApplicationProvider.getApplicationContext<Application>()
        val handler = SendAndroidAppIntentDirectiveHandler(context, mock())

        val intent = handler.createIntent(directive)

        assertThat(intent, hasToString(
            "Intent {  }"))
    }
}

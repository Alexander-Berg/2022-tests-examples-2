package com.yandex.io.sdk.directives

import android.content.Intent
import android.net.Uri
import org.junit.Test
import org.junit.runner.RunWith
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.nullValue
import org.json.JSONObject
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class SendAndroidAppIntentDirectiveTest {
    @Test
    fun `fully specified json payload, parseFromJson, all directive fields are initialized`() {
        val payload = """{
            "action":"android.intent.action.VIEW",
            "component": {
                "pkg": "component.package",
                "cls": "component.class"
            },
            "category":"test_category",
            "type":"test_type",
            "uri":"vnd.youtube:dQw4w9WgXcQ",
            "start_type": "SendBroadcast"
        }"""
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))
        assertThat(directive.action, equalTo("android.intent.action.VIEW"))
        assertThat(directive.uri, equalTo(Uri.parse("vnd.youtube:dQw4w9WgXcQ")))
        assertThat(directive.category, equalTo("test_category"))
        assertThat(directive.type, equalTo("test_type"))
        assertThat(directive.component?.pkg, equalTo("component.package"))
        assertThat(directive.component?.cls, equalTo("component.class"))
        assertThat(directive.startType, equalTo(SendAndroidAppIntentDirective.StartType.SEND_BROADCAST))
    }

    @Test
    fun `empty json, parseFromJson, all directive fields are null`() {
        val payload = "{}"
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))

        assertThat(directive.action, nullValue())
        assertThat(directive.category, nullValue())
        assertThat(directive.component, nullValue())
        assertThat(directive.uri, nullValue())
        assertThat(directive.type, nullValue())
        assertThat(directive.startType, equalTo(SendAndroidAppIntentDirective.StartType.START_ACTIVITY))
    }

    @Test
    fun `directive with flags, parseFromJson, flags are parsed correctly`() {
        val payload = """{
            "flags": {
                "FLAG_ACTIVITY_NEW_TASK": true,
                "FLAG_ACTIVITY_FORWARD_RESULT": false,
                "FLAG_ACTIVITY_REQUIRE_DEFAULT": true
            }
        }"""
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))

        assertThat(directive.flags, equalTo(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REQUIRE_DEFAULT))
    }

    @Test
    fun `directive with null component, parseFromJson, exception not thrown`() {
        val payload = """{
            "component": null
        }"""
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))
        assertThat(directive.component, nullValue())
    }

    @Test
    fun `directive with empty component, parseFromJson, exception not thrown`() {
        val payload = """{
            "component": {}
        }"""
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))
        assertThat(directive.component, nullValue())
    }

    @Test
    fun `directive with empty cls and pkg, parseFromJson, exception not thrown`() {
        val payload = """{
            "component": { "cls": null, "pkg": null }
        }"""
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))
        assertThat(directive.component, nullValue())
    }

    @Test
    fun `directive with all fields as null, parseFromJson, exception not thrown`() {
        val payload = """{
            "action": null,
            "component": null,
            "category": null,
            "type": null,
            "uri": null,
            "start_type": null,
            "flags": null
        }"""
        val directive = SendAndroidAppIntentDirective.parseFromJson("42", "test_intent", JSONObject(payload))
        assertThat(directive.component, nullValue())
    }

}

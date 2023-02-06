package ru.yandex.quasar.centaur_app.directives

import android.os.Bundle
import org.junit.Test
import org.junit.runner.RunWith
import org.hamcrest.Matchers.`is` as Is  // NB: this is required for hamcrest to work with Kotlin, duh
import org.robolectric.RobolectricTestRunner
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.*
import ru.yandex.quasar.centaur_app.BaseTest

@RunWith(RobolectricTestRunner::class)
class SendAndroidAppIntentUnitTest: BaseTest() {
    @Test
    fun testOnlyAction() {
        val parsed = SendAndroidAppIntentDirectivePayload.parse("""{"action":"android.intent.action.MAIN"}""")

        assertThat(parsed, hasToString("Intent { act=android.intent.action.MAIN }"))
    }

    @Test
    fun testParsingSmoke() {
        val parsed = SendAndroidAppIntentDirectivePayload.parse("""{"action":"android.intent.action.VIEW","category":"","component":null,"type":"","uri":"vnd.youtube:dQw4w9WgXcQ"}""")

        assertThat(parsed, hasToString("Intent { act=android.intent.action.VIEW dat=vnd.youtube:dQw4w9WgXcQ }"))
    }

    @Test
    fun testParsingType() {
        val parsed = SendAndroidAppIntentDirectivePayload.parse("""{"action":"android.intent.action.VIEW","category":"","component":null,"type":"text/html","uri":"vnd.youtube:dQw4w9WgXcQ"}""")

        assertThat(parsed, hasToString("Intent { act=android.intent.action.VIEW dat=vnd.youtube:dQw4w9WgXcQ typ=text/html }"))
    }

    @Test
    fun testParsingCat() {
        val parsed = SendAndroidAppIntentDirectivePayload.parse("""{"action":"android.intent.action.VIEW","category":"some_cat","component":null,"type":"","uri":"vnd.youtube:dQw4w9WgXcQ"}""")

        assertThat(parsed, hasToString("Intent { act=android.intent.action.VIEW cat=[some_cat] dat=vnd.youtube:dQw4w9WgXcQ }"))
    }

    @Test
    fun testParsingBoolExtra() {
        val parsed = SendAndroidAppIntentDirectivePayload.parse("""{"action":"A","uri":"U:R", "extras": {"foo": {"single_value": {"bool_value": true}}}}""")

        assertThat(parsed, hasToString("Intent { act=A dat=U:R (has extras) }"))
        assertThat(parsed.extras!!.getBoolean("foo"), Is(true))
    }

    @Test
    fun testParsingBoolArrayExtra() {
        val parsed = SendAndroidAppIntentDirectivePayload.parse("""{"action":"A","uri":"U:R", "extras": {"foo": {"array_value": [{"bool_value": true}, {"bool_value": false}]}}}""")

        assertThat(parsed, hasToString("Intent { act=A dat=U:R (has extras) }"))
        assertThat(parsed.extras!!.getBooleanArray("foo"), Is(booleanArrayOf(true, false)))
    }

    @Test fun extraChar() { assertThat(checkParse(""" "char_value": "a" """).getChar("foo"), Is('a')) }

    @Test fun extraString() { assertThat(checkParse(""" "string_value": "a" """).getString("foo"), Is("a")) }

    @Test fun extraByte() { assertThat(checkParse(""" "byte_value": 1 """).getByte("foo"), Is(1)) }

    @Test fun extraShort() { assertThat(checkParse(""" "short_value": 257 """).getShort("foo"), Is(257)) }

    @Test fun extraInt() { assertThat(checkParse(""" "int_value": 1025 """).getInt("foo"), Is(1025)) }

    @Test fun extraLong() { assertThat(checkParse(""" "long_value": 9223372036854775807 """).getLong("foo"), Is(Long.MAX_VALUE)) }

    @Test fun extraFloat() { assertThat(checkParse(""" "float_value": 123.456 """).getFloat("foo"), Is(123.456F)) }

    @Test fun extraDouble() { assertThat(checkParse(""" "double_value": 3.14 """).getDouble("foo"), Is(3.14)) }

    @Test fun extraCharArray() { assertThat(checkParseArray(""" "char_value": "a" """).getCharArray("foo"), Is(charArrayOf('a', 'a'))) }

    @Test fun extraStringArray() { assertThat(checkParseArray(""" "string_value": "a" """).getStringArrayList("foo"), Is(arrayListOf("a", "a"))) }

    @Test fun extraByteArray() { assertThat(checkParseArray(""" "byte_value": 1 """).getByteArray("foo"), Is(byteArrayOf(1, 1))) }

    @Test fun extraShortArray() { assertThat(checkParseArray(""" "short_value": 257 """).getShortArray("foo"), Is(shortArrayOf(257, 257))) }

    @Test fun extraIntArray() { assertThat(checkParseArray(""" "int_value": 1025 """).getIntArray("foo"), Is(intArrayOf(1025, 1025))) }

    @Test fun extraLongArray() { assertThat(checkParseArray(""" "long_value": 9223372036854775807 """).getLongArray("foo"), Is(longArrayOf(Long.MAX_VALUE, Long.MAX_VALUE))) }

    @Test fun extraFloatArray() { assertThat(checkParseArray(""" "float_value": 123.456 """).getFloatArray("foo"), Is(floatArrayOf(123.456F, 123.456F))) }

    @Test fun extraDoubleArray() { assertThat(checkParseArray(""" "double_value": 3.14 """).getDoubleArray("foo"), Is(doubleArrayOf(3.14, 3.14))) }


    companion object {
        private fun checkParse(extras: String): Bundle {
            return SendAndroidAppIntentDirectivePayload.parse("""{"action":"A","uri":"U:R", "extras": {"foo": {"single_value": {$extras}}}}""").extras!!
        }


        private fun checkParseArray(extras: String): Bundle {
            return SendAndroidAppIntentDirectivePayload.parse("""{"action":"A","uri":"U:R", "extras": {"foo": {"array_value": [{$extras}, {$extras}]}}}""").extras!!
        }
    }
    // TODO: tests for extras
}

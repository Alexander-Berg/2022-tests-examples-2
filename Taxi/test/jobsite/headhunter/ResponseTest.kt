package jobsite.headhunter

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Contact
import ru.yandex.taxi.crm.masshire.search.jsonParser

internal class ResponseTest {
    private val parser = jsonParser()
    private inline fun <reified T> parseAs(json: String): T? {
        return parser.readValue(json, Contact::class.java) as? T
    }

    @Nested
    inner class ContactTest {
        @Test
        fun `contact without type is deserialized to UnknownContact`() {
            val contact = parseAs<Contact.UnknownContact>("""{}""")

            assertNotNull(contact)
        }

        @Test
        fun `contact without type id is deserialized to UnknownContact`() {
            val contact =
                parseAs<Contact.UnknownContact>(
                    """{
                        "type": {"name": "Мобильный телефон"}
                    }"""
                )

            assertNotNull(contact)
        }

        @Test
        fun `contact with unknown type id is deserialized to UnknownContact`() {
            val contact =
                parseAs<Contact.UnknownContact>(
                    """{
                        "type": {"id": "ICQ"}
                    }"""
                )

            assertNotNull(contact)
        }

        @Test
        fun `phone without value is deserialized to phone with null value`() {
            val phone = parseAs<Contact.Phone>("""{ "type": { "id": "cell" } }""")

            assertNotNull(phone)
            assertNull(phone?.value)
        }

        @Test
        fun `phone with null value is deserialized to phone with null value`() {
            val phone =
                parseAs<Contact.Phone>(
                    """{
                        "type": { "id": "cell" },
                        "value": null
                    }"""
                )

            assertNotNull(phone)
            assertNull(phone?.value)
        }

        @Test
        fun `phone with valid value is deserialized to phone with value`() {
            val phone =
                parseAs<Contact.Phone>(
                    """{
                        "type": { "id": "cell" },
                        "value": { "formatted": "+71234567890" }
                    }"""
                )

            assertEquals("+71234567890", phone?.value?.formatted)
        }

        @Test
        fun `phone without comment is deserialized to phone with null comment`() {
            val phone = parseAs<Contact.Phone>("""{ "type": { "id": "cell" } }""")

            assertNotNull(phone)
            assertNull(phone?.comment)
        }

        @Test
        fun `phone with null comment is deserialized to phone with null comment`() {
            val phone =
                parseAs<Contact.Phone>(
                    """{
                        "type": { "id": "cell" },
                        "comment": null
                    }"""
                )

            assertNotNull(phone)
            assertNull(phone?.comment)
        }

        @Test
        fun `phone with valid comment is deserialized to phone with comment`() {
            val phone =
                parseAs<Contact.Phone>(
                    """{
                        "type": { "id": "cell" },
                        "comment": "10:00-20:00"
                    }"""
                )

            assertEquals("10:00-20:00", phone?.comment)
        }

        @Test
        fun `email without value is deserialized to email with null value`() {
            val email =
                parseAs<Contact.Email>(
                    """{
                        "type": { "id": "email" }
                    }"""
                )

            assertNotNull(email)
            assertNull(email?.value)
        }

        @Test
        fun `email with null value is deserialized to email with null value`() {
            val email =
                parseAs<Contact.Email>(
                    """{
                        "type": { "id": "email" },
                        "value": null
                    }"""
                )

            assertNotNull(email)
            assertNull(email?.value)
        }

        @Test
        fun `email with valid value is deserialized to email with value`() {
            val email =
                parseAs<Contact.Email>(
                    """{
                        "type": { "id": "email" },
                        "value": "john.doe@example.com"
                    }"""
                )

            assertNotNull(email)
            assertEquals("john.doe@example.com", email?.value)
        }
    }
}

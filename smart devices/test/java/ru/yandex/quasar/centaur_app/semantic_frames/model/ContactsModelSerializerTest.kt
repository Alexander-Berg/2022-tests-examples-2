package ru.yandex.quasar.centaur_app.semantic_frames.model

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.JsonArray
import com.google.gson.JsonObject
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.core.IsEqual
import org.junit.Test
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.centaur_app.semantic_frames.model.ContactsModel.ContactInfo
import ru.yandex.quasar.centaur_app.semantic_frames.model.ContactsModel.RequestData
import ru.yandex.quasar.centaur_app.semantic_frames.model.ContactsModel.UploadContactsWrapper
import ru.yandex.quasar.centaur_app.semantic_frames.model.ContactsModel.UpdateContactsWrapper
import kotlin.random.Random

class ContactsModelSerializerTest : BaseTest() {
    private val gson: Gson = GsonBuilder()
        .registerTypeHierarchyAdapter(ContactInfo::class.java, ContactInfo.Serializer())
        .create()

    private fun initContacts(count: Int = 3): List<ContactInfo> {
        val result = mutableListOf<ContactInfo>()
        for (i in 1..count) {
            val contact = ContactInfo.TelegramContactInfo(
                Random.nextLong(0, Long.MAX_VALUE).toString(),
                Random.nextLong(0, Long.MAX_VALUE).toString(),
                "Тестовое имя (test name)",
                "Тестовая фамилия (test surname)"
            )
            result.add(contact)
        }

        return result
    }

    private fun assertUploadJsonWrapper(json: JsonObject) {
        assert(json.has("upload_request"))
        assert(json["upload_request"].isJsonObject)
        assert(json["upload_request"].asJsonObject.has("request_value"))
    }

    private fun assertUpdateJsonWrapper(json: JsonObject) {
        assert(json.has("update_request"))
        assert(json["update_request"].isJsonObject)
        assert(json["update_request"].asJsonObject.has("request_value"))
    }

    private fun getContactsModelJson(json: JsonObject): JsonObject {
        assertUploadJsonWrapper(json)
        return json["upload_request"].asJsonObject["request_value"].asJsonObject
    }

    private fun validateContactsModel(
        contactsJson: JsonObject,
        contactsModel: ContactsModel
    ) {
        assert(contactsJson.has("created_contacts"))
        if (contactsModel.createdContacts.isNotEmpty()) {
            assert(contactsJson["created_contacts"].isJsonArray)
            validateContactsList(
                contactsJson["created_contacts"].asJsonArray,
                contactsModel.createdContacts
            )
        }

        assert(contactsJson.has("updated_contacts"))
        if (contactsModel.updatedContacts.isNotEmpty()) {
            assert(contactsJson["updated_contacts"].isJsonArray)
            validateContactsList(
                contactsJson["updated_contacts"].asJsonArray,
                contactsModel.updatedContacts
            )
        }

        assert(contactsJson.has("removed_contacts"))
        if (contactsModel.removedContacts.isNotEmpty()) {
            assert(contactsJson["removed_contacts"].isJsonArray)
            validateContactsList(
                contactsJson["removed_contacts"].asJsonArray,
                contactsModel.removedContacts
            )
        }
    }

    private fun validateContactsList(contactsList: JsonArray, contacts: List<ContactInfo>) {
        assertThat(contactsList.size(), IsEqual(contacts.size))
        contactsList.zip(contacts).forEach { pair ->
            val json = pair.first.asJsonObject
            when (val contact = pair.second) {
                is ContactInfo.TelegramContactInfo -> {
                    assert(json.has("telegram_contact_info"))
                    validateTelegramContact(json["telegram_contact_info"].asJsonObject, contact)
                }
            }
        }
    }

    private fun validateTelegramContact(
        contactJson: JsonObject,
        contactInfo: ContactInfo.TelegramContactInfo
    ) {
        assertThat(contactJson["provider"].asString, IsEqual("telegram"))
        assertThat(contactJson["user_id"].asString, IsEqual(contactInfo.userId))
        assertThat(contactJson["contact_id"].asString, IsEqual(contactInfo.contactId))
        assertThat(contactJson["first_name"].asString, IsEqual(contactInfo.firstName))
        assertThat(contactJson["second_name"].asString, IsEqual(contactInfo.secondName))
    }

    @Test
    fun `serialize upload request`() {
        val contactsModel = ContactsModel(
            createdContacts = initContacts(),
            updatedContacts = initContacts(),
            removedContacts = initContacts()
        )

        val uploadRequest = UploadContactsWrapper(RequestData(contactsModel))
        val resultJson = gson.toJsonTree(uploadRequest).asJsonObject
        assertUploadJsonWrapper(resultJson)
    }

    @Test
    fun `serialize update request`() {
        val contactsModel = ContactsModel(
            createdContacts = initContacts(),
            updatedContacts = initContacts(),
            removedContacts = initContacts()
        )

        val uploadRequest = UpdateContactsWrapper(RequestData(contactsModel))
        val resultJson = gson.toJsonTree(uploadRequest).asJsonObject
        assertUpdateJsonWrapper(resultJson)
    }

    @Test
    fun `serialize full contacts model`() {
        val contactsModel = ContactsModel(
            createdContacts = initContacts(),
            updatedContacts = initContacts(),
            removedContacts = initContacts()
        )

        val uploadRequest = UploadContactsWrapper(RequestData(contactsModel))
        val resultJson = gson.toJsonTree(uploadRequest).asJsonObject
        val contactsModelJson = getContactsModelJson(resultJson)
        validateContactsModel(contactsModelJson, contactsModel)
    }

    @Test
    fun `serialize empty contacts model`() {
        val contactsModel = ContactsModel(
            createdContacts = listOf(),
            updatedContacts = listOf(),
            removedContacts = listOf()
        )

        val resultJson = gson.toJsonTree(UploadContactsWrapper(RequestData(contactsModel))).asJsonObject
        val contactsModelJson = getContactsModelJson(resultJson)
        validateContactsModel(contactsModelJson, contactsModel)
    }

    @Test
    fun `serialize partially filled contacts model`() {
        val contactsModel = ContactsModel(
            createdContacts = initContacts(count = 1),
            updatedContacts = listOf(),
            removedContacts = initContacts()
        )

        val resultJson = gson.toJsonTree(UploadContactsWrapper(RequestData(contactsModel))).asJsonObject
        val contactsModelJson = getContactsModelJson(resultJson)
        validateContactsModel(contactsModelJson, contactsModel)
    }
}

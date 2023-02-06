package ru.yandex.taximeter.swagger.utils

import com.google.gson.Gson
import com.google.gson.JsonDeserializationContext
import com.google.gson.JsonDeserializer
import com.google.gson.JsonElement
import ru.yandex.taxi.swagger.test.refadditionalprops.model.CheckResults
import ru.yandex.taxi.swagger.test.refadditionalprops.model.CheckResultsUnsafe
import ru.yandex.taxi.swagger.test.refadditionalprops.model.makeSafe
import java.lang.reflect.Type

class CheckResultsJsonDeserializer(
    private val gson: Gson
) : JsonDeserializer<Map<String, CheckResults>> {

    override fun deserialize(
        json: JsonElement,
        typeOfT: Type,
        context: JsonDeserializationContext
    ): Map<String, CheckResults> {
        val keyValueList = json.asJsonObject
            .entrySet()
            .map { entry ->
                val ticketResultUnsafe =
                    requireNotNull(gson.fromJson(entry.value, CheckResultsUnsafe::class.java))
                val ticketResult = makeSafe(ticketResultUnsafe)
                entry.key to ticketResult
            }
            .toTypedArray()

        return mapOf(*keyValueList)
    }
}
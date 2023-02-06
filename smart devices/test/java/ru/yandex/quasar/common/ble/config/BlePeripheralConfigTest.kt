package ru.yandex.quasar.common.ble.config

import android.os.Build
import com.google.gson.JsonArray
import com.google.gson.JsonObject
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.util.UUID

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.M, Build.VERSION_CODES.P])
class BlePeripheralConfigTest {

    private fun createCharacteristic(uuid: UUID, permissions: ArrayList<String>): JsonObject {
        val result = JsonObject()
        result.addProperty("uuid", uuid.toString())
        val permissionsArray = JsonArray()
        for(permission in permissions) {
            permissionsArray.add(permission)
        }
        result.add("permissions", permissionsArray)

        return result
    }

    @Test
    fun when_blePeripheralConfigContainsGattDefinitions_then_itParsesCorrectly() {
        // Arrange
        val bleConfig = JsonObject()
        val service = JsonObject()
        val serviceUUID = UUID.randomUUID()
        val writeOnlyCharUUID = UUID.randomUUID()
        val readWriteCharUUID = UUID.randomUUID()
        service.addProperty("uuid", serviceUUID.toString())

        val writeCharacteristic = createCharacteristic(writeOnlyCharUUID, arrayListOf("write"))
        val readWriteCharacteristic = createCharacteristic(readWriteCharUUID, arrayListOf("write", "read"))
        val characteristicsDict = JsonObject()
        characteristicsDict.add("writeOnly", writeCharacteristic)
        characteristicsDict.add("readWrite", readWriteCharacteristic)
        service.add("characteristics", characteristicsDict)

        val servicesDict = JsonObject()
        servicesDict.add("service1", service)
        bleConfig.add("services", servicesDict)

        // Act
        val configMap = mapOf("ble" to bleConfig)
        val config = BlePeripheralConfig.fromConfig(configMap)

        // Assert
        Assert.assertEquals(1, config.services.size)
        val actualService = config.services["service1"]


        Assert.assertEquals(serviceUUID, actualService?.uuid)

        Assert.assertEquals(2, actualService?.characteristics?.size)
        val writeOnlyChar = actualService?.characteristics?.get("writeOnly")
        Assert.assertNotNull(writeOnlyChar)
        Assert.assertEquals(writeOnlyCharUUID, writeOnlyChar?.uuid)
        Assert.assertArrayEquals(arrayListOf("write").toArray(), writeOnlyChar?.permissions?.toArray())

        val readWriteChar = actualService?.characteristics?.get("readWrite")
        Assert.assertNotNull(readWriteChar)
        Assert.assertEquals(readWriteCharUUID, readWriteChar?.uuid)
        Assert.assertArrayEquals(arrayListOf("write", "read").toArray(), readWriteChar?.permissions?.toArray())
    }
}

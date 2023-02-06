package ru.yandex.quasar.glagoldemoapp.picker

import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import ru.yandex.quasar.glagol.DiscoveryResultItem
import ru.yandex.quasar.glagoldemoapp.picker.datasync.RegisteredDevice
import ru.yandex.quasar.glagoldemoapp.picker.ui.DeviceData
import ru.yandex.quasar.glagoldemoapp.picker.utils.DeviceLinker
import ru.yandex.quasar.glagol.logger.GLogger
import ru.yandex.quasar.glagol.logger.ILogger

class DeviceLinkerTest {

    @Before
    fun setup() {
        GLogger.setLogger(object : ILogger {
            override fun d(tag: String, msg: String) {}
            override fun e(tag: String, msg: String) {}
            override fun e(tag: String, msg: String, e: Throwable) {}
        })
    }

    @Test
    fun found_twoDatasync() {
        val linker = DeviceLinker()
        val list = ArrayList<RegisteredDevice>()
        list.add(RegisteredDevice("dev1", "dev1", "platform1"))
        list.add(RegisteredDevice("dev2", "dev2", "platform2"))

        linker.onReceivedDevices(list)

        val items = linker.getItems()
        assert(items.size == 2)
        assertEquals(items[0], DeviceData(RegisteredDevice("dev1", "dev1", "platform1")))
        assertEquals(items[1], DeviceData(RegisteredDevice("dev2", "dev2", "platform2")))
    }

    @Test
    fun found_twoDiscovery() {
        val linker = DeviceLinker()
        val list = ArrayList<DiscoveryResultItem>()
        list.add(TestDevice("platform_1", "100"))
        list.add(TestDevice("platform_2", "200"))

        linker.onDiscoveryResults { list }

        val items = linker.getItems()
        assert(items.size == 2)

        var item = items[0]
        assertEquals(item, DeviceData(TestDevice("platform_1", "100")))
        item = items[1]
        assertEquals(item, DeviceData(TestDevice("platform_2", "200")))
    }

    @Test
    fun found_twoDiscovery_threeDiscovery() {
        val linker = DeviceLinker()
        val list = ArrayList<DiscoveryResultItem>()
        list.add(TestDevice("platform_3", "300"))
        list.add(TestDevice("platform_1", "100"))
        linker.onDiscoveryResults { list }

        list.add(TestDevice("platform_2", "200"))
        linker.onDiscoveryResults { list }

        val items = linker.getItems()
        assert(items.size == 3)

        var item = items[0]
        assertEquals(item, DeviceData(TestDevice("platform_1", "100")))
        item = items[1]
        assertEquals(item, DeviceData(TestDevice("platform_2", "200")))
        item = items[2]
        assertEquals(item, DeviceData(TestDevice("platform_3", "300")))
    }

    @Test
    fun found_oneDatasync_oneDiscovery() {
        val linker = DeviceLinker()

        val discoveryItem = TestDevice("platform_1", "100")
        val discoveryList = arrayListOf(discoveryItem) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(RegisteredDevice(discoveryItem.deviceId, "some other name", discoveryItem.platform))

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 1)

        val regItem = RegisteredDevice(discoveryItem.deviceId, "some other name", discoveryItem.platform)
        val testItem = TestDevice("platform_1", "100")
        assertEquals(result[0], DeviceData(regItem, testItem))
    }

    @Test
    fun found_oneDiscovery_oneDatasync() {
        val linker = DeviceLinker()

        val discoveryItem = TestDevice("platform_1", "100")
        val discoveryList = arrayListOf(discoveryItem) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(RegisteredDevice(discoveryItem.deviceId, discoveryItem.name, discoveryItem.platform))

        linker.onDiscoveryResults { discoveryList }
        linker.onReceivedDevices(datasyncList)

        val result = linker.getItems()
        assert(result.size == 1)
        val disItem = TestDevice("platform_1", "100")
        val regItem = RegisteredDevice("100", discoveryItem.name, "platform_1")
        assertEquals(result[0], DeviceData(regItem, disItem))
    }

    @Test
    fun found_twoDatasync_twoDiscovery() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("platform_1", "100")
        val discoveryItem2 = TestDevice("platform_2", "200")
        val discoveryList = arrayListOf(discoveryItem1, discoveryItem2) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(
            RegisteredDevice("100", discoveryItem1.name, discoveryItem1.platform),
            RegisteredDevice("200", discoveryItem2.name, discoveryItem2.platform)
        )

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 2)
        val regDev1 = RegisteredDevice("100", discoveryItem1.name, discoveryItem1.platform)
        val disDev1 = TestDevice("platform_1", "100")
        val regDev2 = RegisteredDevice("200", discoveryItem2.name, discoveryItem2.platform)
        val disDev2 = TestDevice("platform_2", "200")
        assertEquals(result[0], DeviceData(regDev1, disDev1))
        assertEquals(result[1], DeviceData(regDev2, disDev2))
    }

    @Test
    fun found_twoDatasync_oneDiscovery() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("platform_1", "100")
        val discoveryList = arrayListOf(discoveryItem1) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(
            RegisteredDevice("200", "Test Device 1", "platform_123"),
            RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform)
        )

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 2)
        val regDevice1 = RegisteredDevice("200", "Test Device 1", "platform_123")
        val regDevice2 = RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform)
        val disDevice2 = TestDevice("platform_1", "100")
        assertEquals(result[1], DeviceData(regDevice1))
        assertEquals(result[0], DeviceData(regDevice2, disDevice2))
    }

    @Test
    fun found_twoDatasync_oneDiscovery_twoDiscovery() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("platform_1", "100")
        val discoveryItem2 = TestDevice("platform_2", "200")
        var discoveryList = arrayListOf(discoveryItem1) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(
            RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform),
            RegisteredDevice(discoveryItem2.deviceId, discoveryItem2.name, discoveryItem2.platform)
        )

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        discoveryList = arrayListOf(discoveryItem1, discoveryItem2)

        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 2)
        val regDevice1 = RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform)
        val regDevice2 = RegisteredDevice(discoveryItem2.deviceId, discoveryItem2.name, discoveryItem2.platform)
        assertEquals(result[0], DeviceData(regDevice1, discoveryItem1))
        assertEquals(result[1], DeviceData(regDevice2, discoveryItem2))
    }

    @Test
    fun found_oneDiscovery_twoDatasync() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("platform_1", "100")
        val discoveryList = arrayListOf(discoveryItem1) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(
            RegisteredDevice("200","Test Device 1", "platform_123"),
            RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform)
        )

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 2)
        val regDevice1 = RegisteredDevice("200", "Test Device 1", "platform_123")
        val regDevice2 = RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform)
        assertEquals(result[0], DeviceData(regDevice2, discoveryItem1))
        assertEquals(result[1], DeviceData(regDevice1))
    }

    @Test
    fun found_oneDatasync_twoDiscovery() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("platform_1", "100")
        val discoveryItem2 = TestDevice("platform_2", "200")
        val discoveryList = arrayListOf(discoveryItem1, discoveryItem2) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(
            RegisteredDevice(discoveryItem2.deviceId, discoveryItem2.name, discoveryItem2.platform)
        )

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 2)
        val regDevice1 = RegisteredDevice(discoveryItem2.deviceId, discoveryItem2.name, discoveryItem2.platform)
        val regDevice2 = RegisteredDevice(discoveryItem1.deviceId, discoveryItem1.name, discoveryItem1.platform)
        assertEquals(result[0], DeviceData(regDevice2, discoveryItem1))
        assertEquals(result[1], DeviceData(regDevice1, discoveryItem2))
    }

    @Test
    fun found_unmatched_twoDatasync_twoDiscovery_samePlatform() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("platform", "100")
        val discoveryItem2 = TestDevice("platform", "200")
        val discoveryList = arrayListOf(discoveryItem1, discoveryItem2) as Collection<DiscoveryResultItem>

        val registeredDevice1 = RegisteredDevice("300", "dev1", "platform")
        val registeredDevice2 = RegisteredDevice("400", "dev2", "platform")
        val datasyncList = arrayListOf(registeredDevice1, registeredDevice2)

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 4)
        assertEquals(result[0], DeviceData(discoveryItem1))
        assertEquals(result[1], DeviceData(discoveryItem2))
        assertEquals(result[2], DeviceData(registeredDevice1))
        assertEquals(result[3], DeviceData(registeredDevice2))
    }

    @Test
    fun found_unmatched_twoDatasync_oneDiscovery_sameNames_differentPlatforms() {
        val linker = DeviceLinker()

        val discoveryItem1 = TestDevice("p2", "100")
        val discoveryList = arrayListOf(discoveryItem1) as Collection<DiscoveryResultItem>

        val datasyncList = arrayListOf(
            RegisteredDevice("200", discoveryItem1.name, "p0"),
            RegisteredDevice("300", discoveryItem1.name, "p1")
        )

        linker.onReceivedDevices(datasyncList)
        linker.onDiscoveryResults { discoveryList }

        val result = linker.getItems()
        assert(result.size == 3)
        val regDevice1 = RegisteredDevice("200", discoveryItem1.name, "p0")
        val regDevice2 = RegisteredDevice("300", discoveryItem1.name, "p1")
        val regDevice3 = RegisteredDevice("100", discoveryItem1.name, "p2")
        assertEquals(result[0], DeviceData(regDevice3, discoveryItem1))
        assertEquals(result[1], DeviceData(regDevice1))
        assertEquals(result[2], DeviceData(regDevice2))
    }

    @Test
    fun found_twoDatasync_oneDiscovery_then_oneDifferentDiscovery() {
        val linker = DeviceLinker()

        val datasync = arrayListOf(
            RegisteredDevice("1", "name1", "platform1"),
            RegisteredDevice("2", "name2", "platform2")
        )
        linker.onReceivedDevices(datasync)

        val discovery1 = arrayListOf( TestDevice("platform1", "1") ) as Collection<DiscoveryResultItem>
        linker.onDiscoveryResults { discovery1 }

        val discovery2 = arrayListOf( TestDevice("platform2", "2") ) as Collection<DiscoveryResultItem>
        linker.onDiscoveryResults { discovery2 }

        val result = linker.getItems()
        assert(result.size == 2)
        val regItem1 = RegisteredDevice("1", "name1", "platform1")
        assertEquals("Device should be without discovered item", result[0], DeviceData(regItem1))
        val regItem2 = RegisteredDevice("1", "name1", "platform1")
        val disItem2 = TestDevice("platform2", "2")
        assertEquals("Device should be with discovered item", result[1], DeviceData(regItem2, disItem2))
    }

    @Test
    fun found_twoDatasync_oneDiscovery_twoDatasyncAgain() {
        val linker = DeviceLinker()

        val datasyncResult1 = arrayListOf(
            RegisteredDevice("1", "name1", "platform1"),
            RegisteredDevice("2", "name2", "platform2")
        )
        linker.onReceivedDevices(datasyncResult1)

        val discovery1 = arrayListOf( TestDevice("platform1", "1") ) as Collection<DiscoveryResultItem>
        linker.onDiscoveryResults { discovery1 }

        val linkedItems1 = linker.getItems()

        val datasyncResult2 = arrayListOf(
            RegisteredDevice("1", "name1", "platform1"),
            RegisteredDevice("2", "name2", "platform2")
        )
        linker.onReceivedDevices(datasyncResult2)

        val linkedItems2 = linker.getItems()

        assertEquals(linkedItems1, linkedItems2)
    }

}

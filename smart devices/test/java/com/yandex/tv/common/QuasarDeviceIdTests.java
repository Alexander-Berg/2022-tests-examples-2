package com.yandex.tv.common;

import com.yandex.tv.common.device.utils.QuasarUtils;

import org.junit.Assert;
import org.junit.Test;

import java.security.NoSuchAlgorithmException;

public class QuasarDeviceIdTests {

	@Test
	public void testCalcQuasarDeviceId() {

		// server-side generated ids that will be uploaded to quasar backend
		// https://yt.yandex-team.ru/hahn/navigation?path=//home/smarttv/quasar/device_ids_testing

		testDeviceIdGenerator(
				"yandex_tv_hisi351_cvte",
				"d4:9e:3b:d8:6b:dc",
				"2a26a7fd437f998217f7"
		);

		testDeviceIdGenerator(
				"yandex_tv_rt2871_hikeen",
				"7c:82:74:46:b0:60",
				"621c3963080f52d0682d"
		);

		testDeviceIdGenerator(
				"yandex_tv_mt9632_cv",
				"b8:3d:4e:7f:fa:51",
				"cea2379592fb80b1dc65"
		);

		testDeviceIdGenerator(
				"plt",
				"00:00:00:00:00:00",
				"8b8085cce83032eb6bd3"
		);
	}

	private void testDeviceIdGenerator(String platform, String mac, String expectedDeviceId) {
		String deviceId = null;
		try {
			deviceId = QuasarUtils.calcMacDeviceId(platform, mac);
		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
		Assert.assertEquals(expectedDeviceId, deviceId);
	}

}

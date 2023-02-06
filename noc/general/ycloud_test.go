package cauth_test

import (
	"testing"

	"a.yandex-team.ru/noc/puncher/cmd/puncher-rules-cauth/importers/cauth"
)

func TestYCloudExternalProjectId(t *testing.T) {
	if !cauth.IsCloudExternalProjectID(0xf900) {
		t.Errorf("0xf900 is in CLOUD_OVERLAY_PROD_EXTERNAL_NETS block, please check out NOCREQUESTS-14929")
		t.Fail()
	}

	if !cauth.IsCloudExternalProjectID(0xf9ff) {
		t.Errorf("0xf9ff is in CLOUD_OVERLAY_PROD_EXTERNAL_NETS block, please check out NOCREQUESTS-14929")
		t.Fail()
	}

	if cauth.IsCloudExternalProjectID(0xf800) {
		t.Errorf("0xf800 belongs to yandex cloud, please check out NOCREQUESTS-14929")
		t.Fail()
	}

	if cauth.IsCloudExternalProjectID(0xf8ff) {
		t.Error("0xf800 belongs to yandex cloud, please check out NOCREQUESTS-14929")
		t.Fail()
	}
}

func TestIsCloudProjectId(t *testing.T) {
	if cauth.IsCloudProjectID(0xf900) {
		t.Errorf("0xf900 doesn't belong to Yandex Cloud, please check out NOCREQUESTS-14929")
		t.Fail()
	}

	if !cauth.IsCloudProjectID(0xf8f0) {
		t.Errorf("0xf8f0 belongs to Yandex Cloud, please check out NOCREQUESTS-14929")
		t.Fail()
	}
}

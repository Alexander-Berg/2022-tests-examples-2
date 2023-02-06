package model

import (
	"encoding/base64"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/ytc"
	"a.yandex-team.ru/passport/infra/libs/go/keys"
)

func TestSmsItemFromYt(t *testing.T) {
	iv, err := base64.StdEncoding.DecodeString("CP+IZLjDqeBq4AyG")
	require.NoError(t, err)
	text, err := base64.StdEncoding.DecodeString("IOZ13rRXNTwGnJITTSRAxKq6F38=")
	require.NoError(t, err)
	tag, err := base64.StdEncoding.DecodeString("A68GBi74ZSMxLGMDTp5rng==")
	require.NoError(t, err)

	phone := uint64(88005553535)
	uid := uint64(100500)
	ytRow := ytc.YasmsSmsHistoryRow{
		YasmsSmsHistoryRowBase: ytc.YasmsSmsHistoryRowBase{
			GlobalSmsID:   "some_id",
			Action:        "some_action",
			UnixtimeMicro: 1600000000123000,
		},
		Data: ytc.YasmsSmsHistoryData{
			Extra: map[string]interface{}{
				"some": "field",
			},
			EncryptedText: &ytc.EncryptedData{
				Version: 1,
				KeyID:   1,
				Iv:      iv,
				Text:    text,
				Tag:     tag,
				Codec:   nil,
				Size:    nil,
			},
		},
	}

	common, err := smsItemCommonFromYt(&ytRow, nil)
	require.NoError(t, err)
	require.Equal(t, SmsItemCommon{
		SmsItemBase: &SmsItemBase{
			GlobalSmsID: "some_id",
			Action:      "some_action",
			Timestamp:   1600000000.123,
		},
	}, *common)

	keymap := keys.CreateKeyMap()

	_, err = smsItemCommonFromYt(&ytRow, keymap)
	require.Error(t, err)

	err = keymap.AddBase64Key("1", "MWUSYx6eY547SSNiOYijE+cv9B1Beg+bfmCGefam5vE=")
	require.NoError(t, err)

	ytRow.Phone = &phone
	ytRow.UID = &uid
	common, err = smsItemCommonFromYt(&ytRow, keymap)
	require.NoError(t, err)
	require.Equal(t, SmsItemCommon{
		SmsItemBase: &SmsItemBase{
			GlobalSmsID: "some_id",
			Action:      "some_action",
			Timestamp:   1600000000.123,
		},
		Number: "+88005553535",
		UID:    &uid,
		Text:   "Some important text.",
	}, *common)

	full, err := smsItemFromYt(&ytRow, keymap)
	require.NoError(t, err)
	require.Equal(t, SmsItem{
		Common: &SmsItemCommon{
			SmsItemBase: &SmsItemBase{
				GlobalSmsID: "some_id",
				Action:      "some_action",
				Timestamp:   1600000000.123,
			},
			Number: "+88005553535",
			UID:    &uid,
			Text:   "Some important text.",
		},
		Extra: map[string]interface{}{
			"some": "field",
		},
	}, *full)
}

func TestSmsItemsCollector(t *testing.T) {
	collector := NewSmsItemsCollector(nil)
	require.NoError(t, collector.CollectFromYt(&ytc.YasmsSmsHistoryRow{YasmsSmsHistoryRowBase: ytc.YasmsSmsHistoryRowBase{GlobalSmsID: "some_id"}}))
	require.NoError(t, collector.CollectFromYt(&ytc.YasmsSmsHistoryRow{YasmsSmsHistoryRowBase: ytc.YasmsSmsHistoryRowBase{GlobalSmsID: "some_other_id"}}))
	require.EqualValues(t, []*SmsItem{
		{Common: &SmsItemCommon{SmsItemBase: &SmsItemBase{GlobalSmsID: "some_id"}}},
		{Common: &SmsItemCommon{SmsItemBase: &SmsItemBase{GlobalSmsID: "some_other_id"}}},
	}, collector.Finish())
}

func TestSmsItemsByGlobalIDCollector(t *testing.T) {
	collector := NewSmsItemsByGlobalIDCollector(nil)
	require.NoError(t, collector.CollectFromYt(&ytc.YasmsSmsHistoryRow{YasmsSmsHistoryRowBase: ytc.YasmsSmsHistoryRowBase{GlobalSmsID: "some_id", Action: "enqueued"}}))
	require.NoError(t, collector.CollectFromYt(&ytc.YasmsSmsHistoryRow{YasmsSmsHistoryRowBase: ytc.YasmsSmsHistoryRowBase{GlobalSmsID: "some_other_id", Action: "enqueued"}}))
	require.NoError(t, collector.CollectFromYt(&ytc.YasmsSmsHistoryRow{YasmsSmsHistoryRowBase: ytc.YasmsSmsHistoryRowBase{GlobalSmsID: "some_id", Action: "delivered"}}))
	require.EqualValues(t, SmsItemsByGlobalID{
		"some_id": []*SmsItem{
			{Common: &SmsItemCommon{SmsItemBase: &SmsItemBase{GlobalSmsID: "some_id", Action: "enqueued"}}},
			{Common: &SmsItemCommon{SmsItemBase: &SmsItemBase{GlobalSmsID: "some_id", Action: "delivered"}}},
		},
		"some_other_id": []*SmsItem{
			{Common: &SmsItemCommon{SmsItemBase: &SmsItemBase{GlobalSmsID: "some_other_id", Action: "enqueued"}}},
		},
	}, collector.Finish())
}

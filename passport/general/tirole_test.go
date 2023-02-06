package tirole

import (
	"encoding/hex"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tirole/internal/model"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/keys"
)

func TestPrepareTiroleCompressionHeader(t *testing.T) {
	meta := &model.Meta{
		Codec:         "brotli",
		DecodedSize:   36,
		DecodedSha256: "88839244E8C7C426B20729AF1A13AD792C5FA83C7F2FB6ADCFC60DA1B5EF9603",
	}

	require.Equal(
		t,
		"1:brotli:36:88839244E8C7C426B20729AF1A13AD792C5FA83C7F2FB6ADCFC60DA1B5EF9603",
		prepareTiroleCompressionHeader(meta),
	)
}

func TestTirole_CheckSign(t *testing.T) {
	require := require.New(t)

	keyMap, err := keys.CreateKeyMap("1", "aabbccddeeff")
	require.NoError(err)
	require.NoError(keyMap.AddHexKey("3", "deadbeefc0ffee"))

	tirole := new(Tirole)
	tirole.keyMap = keyMap

	blob, _ := hex.DecodeString("1b52000004be9f5bea2f7f188c4df55215319936b188e573e09003875bf30802c0300d36c6a6e30ad5cec98c89d66d0f82e9524dd4fa127cff839256e14672e848c63d10f39d3892b60aa2e0d336")

	roles := model.ActualRoles{
		Blob: blob,
	}

	badCases := []struct {
		Hmac string
		Err  string
	}{
		{
			Hmac: "",
			Err:  "Invalid encoded_hmac format: ''",
		},
		{
			Hmac: "no",
			Err:  "Invalid encoded_hmac format: 'no'",
		},
		{
			Hmac: ":",
			Err:  "Invalid encoded_hmac format: ':'",
		},
		{
			Hmac: "5:",
			Err:  "Invalid encoded_hmac format: '5:'",
		},
		{
			Hmac: "1:xyz",
			Err:  "Invalid encoded_hmac body format: 'xyz'",
		},
		{
			Hmac: "2:xyz",
			Err:  "Invalid encoded_hmac key id: '2'",
		},
		{
			Hmac: "1:130ad5cec98c89d66d0f82e9524dd4fa127cff839256e14672e848c63d10f39d",
			Err:  "encoded_hmac check mismatch",
		},
	}

	for _, c := range badCases {
		roles.Meta.EncodedHmac = c.Hmac
		err = tirole.CheckSign(&roles)
		require.Error(err)
		require.Contains(err.Error(), c.Err)
	}

	roles.Meta.EncodedHmac = "1:b2e8964b8436ca21e9102d8fbcb67119e5e2f851676a9952b9f8f73fbd5b887c"
	require.NoError(tirole.CheckSign(&roles))

	roles.Meta.EncodedHmac = "3:020ac3819edd0cb9492527f3489621833fd1ded42a7880b9e7e58d1645e9aa1e"
	require.NoError(tirole.CheckSign(&roles))
}

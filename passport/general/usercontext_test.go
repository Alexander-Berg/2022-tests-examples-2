package tvmcontext

import (
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/cpp/tvmauth/src/protos"
	"a.yandex-team.ru/library/go/yandex/tvm"
)

const (
	testValidUserTicket1           = "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:KJFv5EcXn9krYk19LCvlFrhMW-R4q8mKfXJXCd-RBVBgUQzCOR1Dx2FiOyU-BxUoIsaU0PiwTjbVY5I2onJDilge70Cl5zEPI9pfab2qwklACq_ZBUvD1tzrfNUr88otBGAziHASJWgyVDkhyQ3p7YbN38qpb0vGQrYNxlk4e2I"
	testZeroTimeUserTicket         = "3:user:CA0QABokCgMIyAMKAgh7EMgDGghiYjpzZXNzMRoIYmI6c2VzczIgEigB:D0CmYVwWg91LDYejjeQ2UP8AeiA_mr1q1CUD_lfJ9zQSEYEOYGDTafg4Um2rwOOvQnsD1JHM4zHyMUJ6Jtp9GAm5pmhbXBBZqaCcJpyxLTEC8a81MhJFCCJRvu_G1FiAgRgB25gI3HIbkvHFUEqAIC_nANy7NFQnbKk2S-EQPGY"
	testExpiredUserTicket          = "3:user:CLEWEPSd29QFGiEKBgjcgKb4DhDcgKb4DhoLYmI6cGFzc3dvcmQgxIt6KAE:Xn_fRulLxPGO6SV9j6I4DnmemW9oF6v5mL-RHX5D-WUpF0-Y8jEMp3G5ZSeguRaJPrQUPJB3bHeUkihsUJXi3S-oLaDX_k7DxegyhdGeJ2rkM4914Gtrnx16t8_5vwX8NFssWSs7SwBWyUdaBrxRM0G_Pwim6_q57cFLPvDjxYc"
	testCornerCaseWithBigIntTicket = "3:user:CA0Q__________9_GiMKBgjahdn3DhDahdn3DhoLYmI6cGFzc3dvcmQg0oXYzAQoAQ:FlsSGwXvRDHIBC70pewzlvtWUDYLW1eMifbXEuDJqOXxOsbm4UfVSMo0OffPn89v-vz3kFHoTJfBJgDQQ9x0iUQ4xZ031l0rCQxrg--eFq2xFt9xJ_btGfQdBaNGhx4X7rt8ppadkn_jkjmEUzVXaDpaAkjY4HzJLNYmqoRkRt8"
)

func TestUserContextWithKeys(t *testing.T) {
	var err error

	_, err = NewUserContext("1:kokoko", tvm.BlackboxProdYateam)
	require.EqualError(t, err, "invalid protobuf in keys")

	_, err = NewUserContext(getKeys(t, "test_keys_bad_user"), tvm.BlackboxProdYateam)
	require.EqualError(t, err, "failed to parse public key: asn1: structure error: tags don't match (16 vs {class:1 tag:22 length:101 isCompound:false}) {optional:false explicit:false application:false private:false defaultValue:<nil> tag:<nil> stringType:0 timeType:0 set:false omitEmpty:false} RWPublicKey @2")

	_, err = NewUserContext(getKeys(t, "test_keys_bad_service"), tvm.BlackboxProdYateam)
	require.NoError(t, err)

	_, err = NewUserContext(getKeys(t, "test_keys_unknowntype_service"), tvm.BlackboxProdYateam)
	require.NoError(t, err)

	_, err = NewUserContext(getKeys(t, "test_keys_unknowntype_user"), tvm.BlackboxProdYateam)
	require.EqualError(t, err, "unsupported public key type: 1")

	_, err = NewUserContext(getKeys(t, "test_keys_only_user"), tvm.BlackboxProdYateam)
	require.NoError(t, err)

	_, err = NewUserContext(getKeys(t, "test_keys_only_service"), tvm.BlackboxProdYateam)
	require.EqualError(t, err, errorNoPublicKeysUser.Error())

	_, err = NewUserContext(getKeys(t, "test_keys_notallenv_user"), tvm.BlackboxProdYateam)
	require.EqualError(t, err, "there is no one public key for env: Stress")

	_, err = NewUserContext(getGoodKeys(t), tvm.BlackboxProdYateam)
	require.NoError(t, err)
}

func TestNewUserContext2(t *testing.T) {
	uc, err := NewUserContext(getGoodKeys(t), tvm.BlackboxTest)
	if err != nil {
		t.Fatal(err)
	}

	ticket, err := uc.CheckTicket(testValidUserTicket1)
	require.NoError(t, err)

	require.EqualValues(t, []tvm.UID{456, 123}, ticket.Uids)
}

func TestUserContext_CheckExpiredTicket(t *testing.T) {
	uc, err := NewUserContext(getGoodKeys(t), tvm.BlackboxTest)
	if err != nil {
		t.Fatal(err)
	}

	_, err = uc.checkTicketOverriddenEnvImpl(
		testExpiredUserTicket,
		tvm.BlackboxTest,
		time.Time{}.AddDate(2000, 0, 0),
	)
	require.EqualError(t,
		err,
		"You are trying to use tickets from TVM-API production with keys from 'unittest'-mode. Key id: 2865",
	)
}

func TestUserContext_CheckZeroTimeTicket(t *testing.T) {
	_, err := parseFromStr(testZeroTimeUserTicket)
	if err == nil {
		t.Fatal(errors.New("zero time ticket passed the test"))
	}
}

func TestUserContext_CheckTicket(t *testing.T) {
	uc, err := NewUserContext(getGoodKeys(t), tvm.BlackboxTest)
	if err != nil {
		t.Fatal(err)
	}

	_, err = uc.CheckTicket("3:kek")
	require.EqualError(t, err, "invalid ticket format")

	_, err = uc.CheckTicket("3:serv:CBAQ__________9_IgcIyYp6EN8B:TyM3QK1A5vMYqt507iKFKp1I1dZO0hdUSogBOloxnehCJ5vZ1-1e_zaxt2kxL9WX9BJQ5Sxcb5PNG_dCELrG22UojArBmllf4iKyoggp9q2MVDwi-DjbEmdofejeN9fCGhqLwdnnhUtkCwW8beF3QWOemLyC1yyRf0k5uPhfOwA")
	require.EqualError(t, err, "wrong ticket type, user-ticket is expected")

	_, err = uc.checkTicketOverriddenEnvImpl(
		"3:user:CA0QlJEGGhAKAwj0AxD0AyDShdjMBCgB:CyEH83HH4B_RnD9pxyaoVu4Bq1xrPr8lJwZL0iUH6n-TlkhUo-q-qalzg29o1Sx7dPyso0mIH6EejAKreVqUwLLht0NpHt4XDWB35VQfTKzL_RuIuxb2APCPQec3_puDPmYdY7H_bgy0rpaSJ72XYWeRG2tatNwM67nChKNrzHQ",
		uc.GetDefaultEnv(),
		time.Time{}.AddDate(2000, 0, 0),
	)
	require.EqualError(t, err, "expired ticket, exp_time 100500, now 978307200")

	_, err = uc.CheckTicket(testValidUserTicket1[:len(testValidUserTicket1)-10])
	require.EqualError(t, err, "invalid base64 in signature")

	_, err = uc.CheckTicket(testValidUserTicket1)
	require.NoError(t, err)
}

/*
When golang converts big.Int to []byte via .Bytes() it strips out zeroes, so we need to prepend them
in the following ugly way

	xbts := x.Bytes()
	if len(xbts) < len(signature) {
		padding := make([]byte, len(signature) - len(xbts))
		xbts = append(padding, xbts...)
	}

check out math/big/int.go, method Bytes(), line 408

The test is for the case
*/
func TestUserContext_CheckTicket2(t *testing.T) {
	uc, err := NewUserContext(getGoodKeys(t), tvm.BlackboxTest)
	if err != nil {
		t.Fatal(err)
	}

	ticket, err := parseFromStr(testCornerCaseWithBigIntTicket)
	if err != nil {
		t.Fatal(err)
	}

	require.NoError(t, uc.checkTicketSignatureWithEnv(ticket, uc.GetDefaultEnv()))

	validKeyID := ticket.Ticket.KeyId
	var id uint32 = 100500
	ticket.Ticket.KeyId = &id
	require.EqualError(t,
		uc.checkTicketSignatureWithEnv(ticket, uc.GetDefaultEnv()),
		"You are trying to use tickets from TVM-API production with keys from 'unittest'-mode. Key id: 100500",
	)

	id = 19
	require.EqualError(t,
		uc.checkTicketSignatureWithEnv(ticket, uc.GetDefaultEnv()),
		"key id for user ticket not found: 19. Maybe keys are too old",
	)

	ticket.Ticket.KeyId = validKeyID

	ticket.Signature = "X"
	require.EqualError(t,
		uc.checkTicketSignatureWithEnv(ticket, uc.GetDefaultEnv()),
		errorInvalidSignatureBase64.Error(),
	)

	ticket.Signature = "Xn_fRulLxPGO6SV9j6I4DnmemW9oF6v5mL-RHX5D-WUpF0-Y8jEMp3G5ZSeguRaJPrQUPJB3bHeUkihsUJXi3S-oLaDX_k7DxegyhdGeJ2rkM4914Gtrnx16t8_5vwX8NFssWSs7SwBWyUdaBrxRM0G_Pwim6_q57cFLPvDjxYc"
	require.EqualError(t,
		uc.checkTicketSignatureWithEnv(ticket, uc.GetDefaultEnv()),
		"internalApply(). invalid signature format - 2",
	)
}

func TestMakeDebugStringUsr(t *testing.T) {
	require.EqualValues(t, "", makeDebugStringForUserTicket(nil))

	exp := int64(17)
	du := uint64(13)
	en := protos.BbEnvType(1)
	tik := &protos.Ticket{
		ExpirationTime: &exp,
		User: &protos.UserTicket{
			DefaultUid: &du,
			Env:        &en,
		},
	}
	for idx := 0; idx < 15; idx++ {
		uid := uint64(idx)
		u := &protos.User{
			Uid: &uid,
		}
		tik.User.Users = append(tik.User.Users, u)
	}
	require.EqualValues(t,
		"ticket_type=user;expiration_time=17;scope=;default_uid=13;uid=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14;env=Test;",
		makeDebugStringForUserTicket(tik),
	)

	for idx := 15; idx < 21; idx++ {
		uid := uint64(idx)
		u := &protos.User{
			Uid: &uid,
		}
		tik.User.Users = append(tik.User.Users, u)
	}
	require.EqualValues(t,
		"ticket_type=user;expiration_time=17;scope=;default_uid=13;uid=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20;env=Test;",
		makeDebugStringForUserTicket(tik),
	)
}

func TestUserTicketHasScope(t *testing.T) {
	ticket := CheckedUserTicket{}
	require.False(t, ticket.HasScope("kek"))

	ticket = CheckedUserTicket{
		Scopes: make([]string, 0),
	}
	require.False(t, ticket.HasScope("kek"))

	ticket = CheckedUserTicket{
		Scopes: []string{"lol"},
	}
	require.False(t, ticket.HasScope("kek"))

	ticket = CheckedUserTicket{
		Scopes: []string{"lol", "kek"},
	}
	require.True(t, ticket.HasScope("kek"))
}

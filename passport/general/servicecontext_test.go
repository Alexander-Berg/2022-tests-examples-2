package tvmcontext

import (
	"io/ioutil"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/cpp/tvmauth/src/protos"
	"a.yandex-team.ru/library/go/test/yatest"
)

const (
	testTicket = "3:serv:CBAQ__________9_IgcIyYp6EN8B:TyM3QK1A5vMYqt507iKFKp1I1dZO0hdUSogBOloxnehCJ5vZ1-1e_zaxt2kxL9WX9BJQ5Sxcb5PNG_dCELrG22UojArBmllf4iKyoggp9q2MVDwi-DjbEmdofejeN9fCGhqLwdnnhUtkCwW8beF3QWOemLyC1yyRf0k5uPhfOwA"
)

func getKeys(t *testing.T, file string) string {
	tvmTestKeys, err := ioutil.ReadFile(yatest.SourcePath("passport/infra/daemons/tvmtool/internal/tvmcontext/gotest/" + file + ".txt"))
	if err != nil {
		t.Fatal(err)
	}

	return string(tvmTestKeys)
}

func getGoodKeys(t *testing.T) string {
	return getKeys(t, "test_keys")
}

func TestServiceContextWithKeys(t *testing.T) {
	var err error

	_, err = NewServiceContext("qwe")
	require.EqualError(t, err, ErrorInvalidKeysFormat.Error())

	_, err = NewServiceContext(getKeys(t, "test_keys_bad_user"))
	require.NoError(t, err)

	_, err = NewServiceContext(getKeys(t, "test_keys_bad_service"))
	require.EqualError(t, err, "failed to parse public key: asn1: structure error: tags don't match (16 vs {class:1 tag:4 length:83 isCompound:false}) {optional:false explicit:false application:false private:false defaultValue:<nil> tag:<nil> stringType:0 timeType:0 set:false omitEmpty:false} RWPublicKey @2")

	_, err = NewServiceContext(getKeys(t, "test_keys_unknowntype_service"))
	require.EqualError(t, err, "unsupported public key type: 1")

	_, err = NewServiceContext(getKeys(t, "test_keys_unknowntype_user"))
	require.NoError(t, err)

	_, err = NewServiceContext(getKeys(t, "test_keys_only_user"))
	require.EqualError(t, err, errorNoPublicKeysService.Error())

	_, err = NewServiceContext(getKeys(t, "test_keys_only_service"))
	require.NoError(t, err)

	_, err = NewServiceContext(getKeys(t, "test_keys_notallenv_user"))
	require.NoError(t, err)

	_, err = NewServiceContext(getGoodKeys(t))
	require.NoError(t, err)
}

func TestNewServiceContext(t *testing.T) {
	ctx, err := NewServiceContext(getGoodKeys(t))
	if err != nil {
		t.Fatal(err)
	}

	parsed, err := parseFromStr(testTicket)
	if err != nil {
		t.Fatal(err)
	}

	/*
		Just to bypass checking the time
	*/
	require.NoError(t, ctx.checkTicketSignature(parsed))

	validKeyID := parsed.Ticket.KeyId
	var id uint32 = 100500
	parsed.Ticket.KeyId = &id

	require.EqualError(t,
		ctx.checkTicketSignature(parsed),
		"You are trying to use tickets from TVM-API production with keys from 'unittest'-mode. Key id: 100500",
	)

	id = 1
	require.EqualError(t,
		ctx.checkTicketSignature(parsed),
		"key id for service ticket not found: 1. Maybe keys are too old",
	)

	parsed.Ticket.KeyId = validKeyID

	parsed.Signature = "X"
	require.EqualError(t, ctx.checkTicketSignature(parsed), errorInvalidSignatureBase64.Error())
	parsed.Signature = "D0CmYVwWg91LDYejjeQ2UP8AeiA_mr1q1CUD_lfJ9zQSEYEOYGDTafg4Um2rwOOvQnsD1JHM4zHyMUJ6Jtp9GAm5pmhbXBBZqaCcJpyxLTEC8a81MhJFCCJRvu_G1FiAgRgB25gI3HIbkvHFUEqAIC_nANy7NFQnbKk2S-EQPGY"
	require.Error(t, ctx.checkTicketSignature(parsed))

}

func TestServiceContext_CheckTicket(t *testing.T) {
	ctx, err := NewServiceContext(getGoodKeys(t))
	require.NoError(t, err)

	_, err = ctx.CheckTicketWithoutDst("3:kek")
	require.EqualError(t, err, "invalid ticket format")

	_, err = ctx.CheckTicketWithoutDst("3:user:CA0Q__________9_GhIKBAiUkQYQlJEGINKF2MwEKAE:G2IuwehIqYE2ZWzpIlcMQGzQ_DzI0Fg-e1bbghEMYXqkyEui8zw3G6-XSHYsBfHCmX0XxIxFMh_q6qVQ55VS5dXyZYIYoYurwMViuaYB20bPwpIVLRpKQ4uec7N2UqXbJAcSRMO_bUWGiGspAjaLhJIvzxM_JxEGatG_V0u4mqw")
	require.EqualError(t, err, errorWrongTicketTypeService.Error())

	_, err = ctx.checkTicketWithoutDstImpl(
		"3:serv:CBAQlJEGIgQICxAW:V56a7U5xqFrhh_aS8yJ2h6QB7iTVk5zlF0yXnYx1b1cqQh05q-JUHwyUzlGTAgRfVwn8kSzr6Hgne7cOHVRG1i-cNSpQfzwAZ4nWhzMGD68r0BtW0Pls5K3RW4tONMyaiHOQGKfFLA0OFdNDz4VXC5MIMN2r2XXjEBhPCuuycAg",
		time.Time{}.AddDate(2000, 0, 0),
	)
	require.EqualError(t, err, "expired ticket, exp_time 100500, now 978307200")

	_, err = ctx.CheckTicketWithoutDst(testTicket[:len(testTicket)-10])
	require.EqualError(t, err, "invalid base64 in signature")

	_, err = ctx.CheckTicketWithoutDst(testTicket)
	require.NoError(t, err)

	_, err = ctx.CheckTicket(testTicket, 13)
	require.EqualError(t, err, "Wrong ticket dst, expected 13, got 223")

	_, err = ctx.CheckTicket(testTicket, 223)
	require.NoError(t, err)
}

func TestMakeDebugStringSrv(t *testing.T) {
	require.EqualValues(t, "", makeDebugStringForServiceTicket(nil))

	expTime := int64(456)
	require.EqualValues(t,
		"ticket_type=service;expiration_time=456;src=0;dst=0;scope=;",
		makeDebugStringForServiceTicket(&protos.Ticket{
			ExpirationTime: &expTime,
		}),
	)
}

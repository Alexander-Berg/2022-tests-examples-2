package knifeunittest

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

const (
	okServiceTicket  = "3:serv:CBAQ__________9_IgYIlJEGECo:UIcs0CBwSTQBM9MUr9kHFDKNfQX9-zQxsiYwGz2CU-ncnMf53rmqXptz-_EQpoTL6WPb61Fk3lWcogi0pib0_WPUhGERDHUkg77Mp_jJllU4b5ncz-lVoGe_OTpeB33Rt1CgIYCtGtjIJZMJhVTz6lQtY9Kl5YWDhyV3QPHnb2M"
	badServiceTicket = "3:serv:CBAQ__________9_IgYIlJEGECo:UIcs0CBwSTQBM9MUr9kHFDKNfQX9-zQxsiYwGz2CU-ncnMf53rmqXptz-_EQpoTL6WPb61Fk3lWcogi0pib0_WPUhGERDHUkg77Mp_jJllU4b5ncz-lVoGe_OTpeB33Rt1CgIYCtGtjIJZMJhVTz6lQtY9Kl5YWDhyV3QPH"
	okUserTicket     = "3:user:CA4Q__________9_GhAKAwjIAxDIAyDShdjMBCgD:97tcJFJK1AmQ6esF9gG9kcqK_wtiHKRq7L3PuTR-SwYJP-Eua4TTadDlQTeW8Pl9QaDk7a6M6yGLlPQE0DgG3VPIJSv1Bgqc3cRSBOncdvxpsdebRjEZ_hiVxXWd4RovkhaArIIWkOFyARrO1fwdsZXAodig0RxAXGodQnwcbw"
	badUserTicket    = "3:user:CA4Q__________9_GhAKAwjIAxDIAyDShdjMBCgD:97tcJFJK1AmQ6esF9gG9kcqK_wtiHKRq7L3PuTR-SwYJP-Eua4TTadDlQTeW8Pl9QaDk7a6M6yGLlPQE0DgG3VPIJSv1Bgqc3cRSBOncdvxpsdebRjEZ_hiVxXWd4RovkhaArIIWkOFyARrO1fwdsZXAodig0RxAXGodQn"
)

func TestServiceChecker(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    unittestSecret,
				SelfTvmID: 42,
				Dsts: map[string]tvmtypes.Dst{
					"he": {ID: 100501},
				},
			},
		},
	}
	ocfg := tvmtypes.NewOptimizedConfig(cfg)

	us, err := NewUnittestState(ocfg, "")
	if err != nil {
		t.Fatal(err)
	}

	sc, err := us.GetServiceContext()
	if err != nil {
		t.Fatal(err)
	}

	pt, err := sc.CheckTicket(okServiceTicket, 42)
	if err != nil {
		t.Fatal(err)
	}
	if pt.SrcID != 100500 {
		t.Fatalf("Unexpected src: %d", pt.SrcID)
	}

	_, err = sc.CheckTicketWithoutDst(badServiceTicket)
	if err == nil {
		t.Fatalf("Ticket must be bad")
	}
}

func TestUserChecker(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    unittestSecret,
				SelfTvmID: 42,
				Dsts: map[string]tvmtypes.Dst{
					"he": {ID: 100501},
				},
			},
		},
	}
	ocfg := tvmtypes.NewOptimizedConfig(cfg)

	us, err := NewUnittestState(ocfg, "")
	if err != nil {
		t.Fatal(err)
	}

	uc, err := us.GetUserContext()
	if err != nil {
		t.Fatal(err)
	}

	pt, err := uc.CheckTicket(okUserTicket)
	require.NoError(t, err)
	require.EqualValues(t, pt.DefaultUID, 456)

	_, err = uc.CheckTicket(badUserTicket)
	require.EqualError(t, err, "internalApply(). invalid signature format - 4")
}

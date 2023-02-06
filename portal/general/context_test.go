package base

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/proto/morda_data"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_context_UpdateCache(t *testing.T) {
	type mocks struct {
		cookieKeeper       *MockcookieKeeper
		domainKeeper       *MockdomainKeeper
		deviceKeeper       *MockdeviceKeeper
		clidKeeper         *MockclidKeeper
		cspKeeper          *MockcspKeeper
		yaCookiesKeeper    *MockyaCookiesKeeper
		geoKeeper          *MockgeoKeeper
		localeKeeper       *MocklocaleKeeper
		aadbKeeper         *MockaadbKeeper
		flagsKeeper        *MockabFlagsKeeper
		requestKeeper      *MockrequestKeeper
		appInfoKeeper      *MockappInfoKeeper
		mordaContentKeeper *MockmordaContentKeeper
		mordazoneKeeper    *MockmordazoneKeeper
		timeKeeper         *MocktimeKeeper
		madmContentKeeper  *MockmadmContentKeeper
		authKeeper         *MockauthKeeper
		yabsKeeper         *MockyabsKeeper
		bigbKeeper         *MockbigbKeeper
		robotKeeper        *MockrobotKeeper

		client *Mockclient
	}

	type fields struct {
		base *morda_data.Base
		auth *morda_data.Auth
		yabs *morda_data.Yabs
		bigb *morda_data.BigB
	}
	tests := []struct {
		name      string
		fields    fields
		initMocks func(mocks)
		wantErr   bool
	}{
		{
			name: "No changes; base cache is warm",
			fields: fields{
				base: &morda_data.Base{Cookie: prepared.TestCookieVer1},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{Cookie: prepared.TestCookieVer1}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in cookie keeper cache; base cache is warm",
			fields: fields{
				base: &morda_data.Base{Cookie: prepared.TestCookieVer1},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(prepared.TestCookieVer2).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{Cookie: prepared.TestCookieVer2}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in mordazone keeper cache; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					MordaZone: &morda_data.MordaZone{
						Value: []byte("ru"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(&morda_data.MordaZone{Value: []byte("net")}).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					MordaZone: &morda_data.MordaZone{
						Value: []byte("net"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in device keeper cache; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					Device: &morda_data.Device{
						BrowserDesc: &morda_data.BrowserDesc{
							Traits: map[string]string{
								"foo": "bar",
							},
						},
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(&morda_data.Device{
					BrowserDesc: &morda_data.BrowserDesc{
						Traits: map[string]string{
							"test": "smth",
						},
					},
				}).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					Device: &morda_data.Device{
						BrowserDesc: &morda_data.BrowserDesc{
							Traits: map[string]string{
								"test": "smth",
							},
						},
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in clid cache; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					Clid: &morda_data.Clid{
						Client: []byte("999999"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(&morda_data.Clid{Client: []byte("1245532")}).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					Clid: &morda_data.Clid{
						Client: []byte("1245532"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in cookie and mordazone cache; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					Cookie: prepared.TestCookieVer2,
					MordaZone: &morda_data.MordaZone{
						Value: []byte("ru"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(prepared.TestCookieVer1).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(&morda_data.MordaZone{Value: []byte("net")}).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					Cookie: prepared.TestCookieVer1,
					MordaZone: &morda_data.MordaZone{
						Value: []byte("net"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in YaCookie; base cache is warm",
			fields: fields{
				base: &morda_data.Base{YaCookies: prepared.TestDTOYaCookiesVer1},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(prepared.TestDTOYaCookiesVer2).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					YaCookies: prepared.TestDTOYaCookiesVer2,
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in locale; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					Locale: &morda_data.Lang{
						Locale: []byte("ru"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(&morda_data.Lang{Locale: []byte("en")}).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					Locale: &morda_data.Lang{
						Locale: []byte("en"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in aadb; base cache is warm",
			fields: fields{
				base: &morda_data.Base{AntiAdblock: &morda_data.AntiAdblock{IsAddBlock: true}},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(&morda_data.AntiAdblock{IsAddBlock: false}).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					AntiAdblock: &morda_data.AntiAdblock{IsAddBlock: false},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in robot; base cache is warm",
			fields: fields{
				base: &morda_data.Base{Robot: &morda_data.Robot{
					IsRobot: true,
				}},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(&morda_data.Robot{IsRobot: false}).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{Robot: &morda_data.Robot{
					IsRobot: false,
				}}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in request; base cache is warm",
			fields: fields{
				base: &morda_data.Base{Request: &morda_data.Request{
					IsInternal:   true,
					IsStaffLogin: false,
				}},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(&morda_data.Request{
					IsInternal:   false,
					IsStaffLogin: true,
				}).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{Request: &morda_data.Request{
					IsInternal:   false,
					IsStaffLogin: true,
				}}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in appInfo; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					AppInfo: &morda_data.AppInfo{
						Id:       []byte("ru.yandex.mobile"),
						Version:  []byte("60000000"),
						Platform: []byte("iphone"),
						Uuid:     []byte("987654321"),
						Did:      []byte("123456789"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(&morda_data.AppInfo{
					Id:       []byte("ru.yandex.searchplugin"),
					Version:  []byte("78000000"),
					Platform: []byte("android"),
					Uuid:     []byte("123456789"),
					Did:      []byte("987654321"),
				}).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					AppInfo: &morda_data.AppInfo{
						Id:       []byte("ru.yandex.searchplugin"),
						Version:  []byte("78000000"),
						Platform: []byte("android"),
						Uuid:     []byte("123456789"),
						Did:      []byte("987654321"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in mordaContent; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					MordaContent: &morda_data.MordaContent{
						Value: []byte("big"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(&morda_data.MordaContent{
					Value: []byte("touch"),
				}).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					MordaContent: &morda_data.MordaContent{
						Value: []byte("touch"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "Changes in madmContent; base cache is warm",
			fields: fields{
				base: &morda_data.Base{
					MadmContent: &morda_data.MadmContent{
						Values: [][]byte{
							[]byte("big"),
							[]byte("touch_only"),
						},
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(&morda_data.MadmContent{
					Values: [][]byte{
						[]byte("api_search_2"),
						[]byte("all"),
					},
				}).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(&morda_data.Base{
					MadmContent: &morda_data.MadmContent{
						Values: [][]byte{
							[]byte("api_search_2"),
							[]byte("all"),
						},
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "changes in YABS; base cache is warm",
			fields: fields{
				yabs: &morda_data.Yabs{
					BkFlags: map[string]*morda_data.Yabs_BkFlag{
						"flag_AAA": {
							ClickUrl: []byte("click_url_aaa"),
							CloseUrl: []byte("close_url_aaa"),
							LinkNext: []byte("link_next_aaa"),
						},
						"flag_BBB": {
							ClickUrl: []byte("click_url_bbb"),
							CloseUrl: []byte("close_url_bbb"),
							LinkNext: []byte("link_next_bbb"),
						},
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(&morda_data.Yabs{
					BkFlags: map[string]*morda_data.Yabs_BkFlag{
						"flag_CCC": {
							ClickUrl: []byte("click_url_ccc"),
							CloseUrl: []byte("close_url_ccc"),
							LinkNext: []byte("link_next_ccc"),
						},
						"flag_DDD": {
							ClickUrl: []byte("click_url_ddd"),
							CloseUrl: []byte("close_url_ddd"),
							LinkNext: []byte("link_next_ddd"),
						},
					},
				}).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(&morda_data.Yabs{
					BkFlags: map[string]*morda_data.Yabs_BkFlag{
						"flag_CCC": {
							ClickUrl: []byte("click_url_ccc"),
							CloseUrl: []byte("close_url_ccc"),
							LinkNext: []byte("link_next_ccc"),
						},
						"flag_DDD": {
							ClickUrl: []byte("click_url_ddd"),
							CloseUrl: []byte("close_url_ddd"),
							LinkNext: []byte("link_next_ddd"),
						},
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "changes in BigB; base cache is warm",
			fields: fields{
				bigb: prepared.TestDTOBigBVer1,
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(nil).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(prepared.TestDTOBigBVer2).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(prepared.TestDTOBigBVer2).Return(nil).Times(1)
			},
			wantErr: false,
		},
		{
			name: "changes in Auth; base cache is warm",
			fields: fields{
				auth: &morda_data.Auth{
					UID: []byte("123"),
					Sids: map[string][]byte{
						"a": []byte("abc"),
						"b": []byte("bcd"),
					},
				},
			},
			initMocks: func(mocks mocks) {
				mocks.cookieKeeper.EXPECT().GetCookieIfUpdated().Return(nil).Times(1)
				mocks.domainKeeper.EXPECT().GetDomainIfUpdated().Return(nil).Times(1)
				mocks.deviceKeeper.EXPECT().GetDeviceIfUpdated().Return(nil).Times(1)
				mocks.clidKeeper.EXPECT().GetClidIfUpdated().Return(nil).Times(1)
				mocks.cspKeeper.EXPECT().GetCSPIfUpdated().Return(nil).Times(1)
				mocks.yaCookiesKeeper.EXPECT().GetYaCookiesIfUpdated().Return(nil).Times(1)
				mocks.geoKeeper.EXPECT().GetGeoIfUpdated().Return(nil).Times(1)
				mocks.localeKeeper.EXPECT().GetLocaleIfUpdated().Return(nil).Times(1)
				mocks.aadbKeeper.EXPECT().GetAntiAdblockIfUpdated().Return(nil).Times(1)
				mocks.flagsKeeper.EXPECT().GetFlagsIfUpdated().Return(nil).Times(1)
				mocks.requestKeeper.EXPECT().GetRequestIfUpdated().Return(nil).Times(1)
				mocks.appInfoKeeper.EXPECT().GetAppInfoIfUpdated().Return(nil).Times(1)
				mocks.mordaContentKeeper.EXPECT().GetMordaContentIfUpdated().Return(nil).Times(1)
				mocks.mordazoneKeeper.EXPECT().GetMordaZoneIfUpdated().Return(nil).Times(1)
				mocks.timeKeeper.EXPECT().GetTimeIfUpdated().Return(nil).Times(1)
				mocks.madmContentKeeper.EXPECT().GetMadmContentIfUpdated().Return(nil).Times(1)
				mocks.authKeeper.EXPECT().GetAuthIfUpdated().Return(&morda_data.Auth{
					UID: []byte("789"),
					Sids: map[string][]byte{
						"c": []byte("cde"),
						"d": []byte("def"),
					},
				}).Times(1)
				mocks.yabsKeeper.EXPECT().GetYabsIfUpdated().Return(nil).Times(1)
				mocks.bigbKeeper.EXPECT().GetBigBIfUpdated().Return(nil).Times(1)
				mocks.robotKeeper.EXPECT().GetRobotIfUpdated().Return(nil).Times(1)

				mocks.client.EXPECT().Set(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetAuth(&morda_data.Auth{
					UID: []byte("789"),
					Sids: map[string][]byte{
						"c": []byte("cde"),
						"d": []byte("def"),
					},
				}).Return(nil).Times(1)
				mocks.client.EXPECT().SetYabs(nil).Return(nil).Times(1)
				mocks.client.EXPECT().SetBigB(nil).Return(nil).Times(1)
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {

			ctrl := gomock.NewController(t)

			mocks := mocks{
				cookieKeeper:       NewMockcookieKeeper(ctrl),
				domainKeeper:       NewMockdomainKeeper(ctrl),
				deviceKeeper:       NewMockdeviceKeeper(ctrl),
				clidKeeper:         NewMockclidKeeper(ctrl),
				cspKeeper:          NewMockcspKeeper(ctrl),
				yaCookiesKeeper:    NewMockyaCookiesKeeper(ctrl),
				geoKeeper:          NewMockgeoKeeper(ctrl),
				localeKeeper:       NewMocklocaleKeeper(ctrl),
				aadbKeeper:         NewMockaadbKeeper(ctrl),
				flagsKeeper:        NewMockabFlagsKeeper(ctrl),
				requestKeeper:      NewMockrequestKeeper(ctrl),
				appInfoKeeper:      NewMockappInfoKeeper(ctrl),
				mordaContentKeeper: NewMockmordaContentKeeper(ctrl),
				mordazoneKeeper:    NewMockmordazoneKeeper(ctrl),
				timeKeeper:         NewMocktimeKeeper(ctrl),
				madmContentKeeper:  NewMockmadmContentKeeper(ctrl),
				authKeeper:         NewMockauthKeeper(ctrl),
				yabsKeeper:         NewMockyabsKeeper(ctrl),
				bigbKeeper:         NewMockbigbKeeper(ctrl),
				robotKeeper:        NewMockrobotKeeper(ctrl),
				client:             NewMockclient(ctrl),
			}

			if tt.initMocks != nil {
				tt.initMocks(mocks)
			}

			c := &context{
				cookieKeeper:       mocks.cookieKeeper,
				domainKeeper:       mocks.domainKeeper,
				deviceKeeper:       mocks.deviceKeeper,
				clidKeeper:         mocks.clidKeeper,
				cspKeeper:          mocks.cspKeeper,
				yaCookiesKeeper:    mocks.yaCookiesKeeper,
				geoKeeper:          mocks.geoKeeper,
				localeKeeper:       mocks.localeKeeper,
				aadbKeeper:         mocks.aadbKeeper,
				abFlagsKeeper:      mocks.flagsKeeper,
				requestKeeper:      mocks.requestKeeper,
				appInfoKeeper:      mocks.appInfoKeeper,
				mordaContentKeeper: mocks.mordaContentKeeper,
				mordazoneKeeper:    mocks.mordazoneKeeper,
				madmContentKeeper:  mocks.madmContentKeeper,
				timeKeeper:         mocks.timeKeeper,
				authKeeper:         mocks.authKeeper,
				yabsKeeper:         mocks.yabsKeeper,
				bigbKeeper:         mocks.bigbKeeper,
				robotKeeper:        mocks.robotKeeper,
				client:             mocks.client,
				base:               tt.fields.base,
				yabs:               tt.fields.yabs,
				bigb:               tt.fields.bigb,
				auth:               tt.fields.auth,
			}

			err := c.UpdateCache()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

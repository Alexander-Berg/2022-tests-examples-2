package recognizers_test

import (
	"testing"

	"github.com/stretchr/testify/suite"
	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies/mocks"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/recognizers"
)

type MOXATestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *MOXATestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *MOXATestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeMoxaOutput() map[string]string {
	return map[string]string{
		"cat /proc/version":        moxaVersion,
		"sudo opkg list-installed": opkgList,
	}
}

func (suite *MOXATestSuite) TestSuccessRecognizeMOXA() {
	expectedSoft := MoxaSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "moxa",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeMoxaOutput()
	rec, err := recognizers.RecognizeMOXA("moxa", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().Equal(len(expectedSoft.Files), len(rec.RecognizedSoft.Files))
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestMOXATestSuite(t *testing.T) {
	suite.Run(t, new(MOXATestSuite))
}

var moxaVersion = `cat /proc/version
Linux version 2.6.39 (root@42ed3b42e4a5) (gcc version 4.8.4 (OpenWrt GCC 4.8.4 r9125-eab92cb2a6) ) #0 Thu Mar 3 12:07:50 2022

`

var opkgList = `$ sudo opkg list-installed
base-files - 196-r9125-eab92cb2a6
busybox - 1.30.0-3
cdpd - 49d79941-1
chattr - 1.44.3-1
conserver - 8.2.2-1
dmesg - 2.33-1
dropbear - 2017.75-9
dropbearconvert - 2017.75-9
e2fsprogs - 1.44.3-1
evgetch - 1
fdisk - 2.33-1
firewall - 2017-11-07-c4309372-1
fstools - 2018-12-28-af93f4b8-3
fwtool - 1
gdbserver - 8.2.1-1
hwclock - 2.33-1
ip6tables - 1.4.4-1
iptables - 1.4.4-1
iptables-mod-conntrack - 1.4.4-1
iptables-mod-conntrack-extra - 1.4.4-1
jshn - 2018-07-25-c83a84af-2
jsonfilter - 2018-02-04-c7e938d6-1
kernel - 2.6.39-1-777862b729930649ec4f7c64865b7bea
kexec - 2.0.16-1
kexec-tools - 2.0.16-1
kmod-bridge - 2.6.39-1
kmod-ip6tables - 2.6.39-1
kmod-ipt-conntrack - 2.6.39-1
kmod-ipt-conntrack-extra - 2.6.39-1
kmod-ipt-core - 2.6.39-1
kmod-ipt-nat - 2.6.39-1
kmod-lib-crc-ccitt - 2.6.39-1
kmod-llc - 2.6.39-1
kmod-nf-conntrack - 2.6.39-1
kmod-nf-conntrack6 - 2.6.39-1
kmod-nf-ipt - 2.6.39-1
kmod-nf-ipt6 - 2.6.39-1
kmod-nf-nat - 2.6.39-1
kmod-nf-nathelper - 2.6.39-1
kmod-nf-reject - 2.6.39-1
kmod-nf-reject6 - 2.6.39-1
kmod-stp - 2.6.39-1
libblkid - 2.33-1
libblobmsg-json - 2018-07-25-c83a84af-2
libc - 1.1.20-1
libcomerr - 1.44.3-1
libext2fs - 1.44.3-1
libfdisk - 2.33-1
libgcc - 4.8.4-1
libiptc1.4.4 - 1.4.4-1
libjson-c - 0.12.1-2
libjson-script - 2018-07-25-c83a84af-2
libncurses6 - 6.1-1
libnl-tiny - 0.1-5
libopenssl1.0.0 - 1.0.2p-1
libpcap - 1.9.0-1
libpopt - 1.16-1
libpthread - 1.1.20-1
librt - 1.1.20-1
libsmartcols - 2.33-1
libss - 1.44.3-1
libubox20170601 - 2018-07-25-c83a84af-2
libubus20170705 - 2018-10-06-221ce7e7-1
libuci - 2018-08-11-4c8b4d6e-1
libuclient20181124 - 2018-11-24-3ba74ebc-1
libuuid - 2.33-1
libxtables1.4.4 - 1.4.4-1
logd - 2018-12-18-876c7f5b-1
mtd - 23
netifd - 2018-12-16-2750ce2e-1
openwrt-keyring - 2018-05-18-103a32e9-1
opkg - 2019-01-18-7708a01a-1
procd - 2018-11-23-d6673547-1
rsync - 3.2.3-3
screen - 4.8.0-2
strace - 4.25-1
sudo - 1.9.10
tcpdump - 4.9.2-1
terminfo - 6.1-1
ubox - 2018-12-18-876c7f5b-1
ubus - 2018-10-06-221ce7e7-1
ubusd - 2018-10-06-221ce7e7-1
uci - 2018-08-11-4c8b4d6e-1
uclient-fetch - 2018-11-24-3ba74ebc-1
usign - 2015-07-04-ef641914-1
zlib - 1.2.11-2
`

var MoxaSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "MOXA/r9125-eab92cb2a6.ymal",
	Type: ptr.String(`moxa`),
	Files: []entities.SoftFile{
		{
			Type:     ptr.String(`main`),
			FileName: ptr.String(`base-files: r9125`),
			Version:  ptr.String(`r9125`),
		},
		{
			Type:     ptr.String(`kernel`),
			FileName: ptr.String(`kernel: 2.6.39-1-777862b729930649ec4f7c64865b7bea`),
			Version:  ptr.String(`2.6.39-1-777862b729930649ec4f7c64865b7bea`),
		},
		{
			Type:     ptr.String(`cdpd`),
			FileName: ptr.String(`cdpd: 49d79941-1`),
			Version:  ptr.String(`49d79941-1`),
		},
		{
			Type:     ptr.String(`libgcc`),
			FileName: ptr.String(`libgcc: 4.8.4-1`),
			Version:  ptr.String(`4.8.4-1`),
		},
		{
			Type:     ptr.String(`evgetch`),
			FileName: ptr.String(`evgetch: 1`),
			Version:  ptr.String(`1`),
		},
		{
			Type:     ptr.String(`conserver`),
			FileName: ptr.String(`conserver: 8.2.2-1`),
			Version:  ptr.String(`8.2.2-1`),
		},
		{
			Type:     ptr.String(`libopenssl1.0.0`),
			FileName: ptr.String(`libopenssl1.0.0: 1.0.2p-1`),
			Version:  ptr.String(`1.0.2p-1`),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		{
			Type:     `main`,
			FileName: `base-files: r9125`,
		}: {},
		{
			Type:     `kernel`,
			FileName: `kernel: 2.6.39-1-777862b729930649ec4f7c64865b7bea`,
		}: {},
		{
			Type:     `cdpd`,
			FileName: `cdpd: 49d79941-1`,
		}: {},
		{
			Type:     `libgcc`,
			FileName: `libgcc: 4.8.4-1`,
		}: {},
		{
			Type:     `evgetch`,
			FileName: `evgetch: 1`,
		}: {},
		{
			Type:     `conserver`,
			FileName: `conserver: 8.2.2-1`,
		}: {},
		{
			Type:     `libopenssl1.0.0`,
			FileName: `libopenssl1.0.0: 1.0.2p-1`,
		}: {},
	},
	Deprecated: false,
}

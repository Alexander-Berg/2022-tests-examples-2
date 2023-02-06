package crypto

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"errors"
	"log"
	"strings"
	"testing"
)

const (
	testPubKey = "MIIBBQKCAQEA4RATOfumLD1n6ICrW5biaAl9VldinczmkNPjpUWwc3gs8PnkCrtdnPFmpBwW3gjHdSNU1OuEg5A6K1o1xiGv9sU-jd88zQBOdK6E2zwnJnkK6bNusKE2H2CLqg3aMWCmTa9JbzSy1uO7wa-xCqqNUuCko-2lyv12HhL1ICIH951SHDa4qO1U5xZhhlUAnqWi9R4tYDeMiF41WdOjwT2fg8UkbusThmxa3yjCXjD7OyjshPtukN8Tl3UyGtV_s2CLnE3f28VAi-AVW8FtgL22xbGhuyEplXRrtF1E5oV7NSqxH1FS0SYROA8ffYQGV5tfx5WDFHiXDEP6BzoVfeBDRQ"

	testSignaturePubKey     = "MIIBBAKCAQBwsRd4frsVARIVSfj_vCdfvA3Q9SsGhSybdBDhbm8L6rPqxdoSNLCdNXzDWj7Ppf0o8uWHMxC-5Lfw0I18ri68nhm9-ndixcnbn6ti1uetgkc28eiEP6Q8ILD_JmkynbUl1aKDNAa5XsK2vFSEX402uydRomsTn46kRY23hfqcIi0ohh5VxIrpclRsRZus0JFu-RJzhqTbKYV4y4dglWPGHh5BuTv9k_Oh0_Ra8Xp5Rith5vjaKZUQ5Hyh9UtBYTkNWdvXP9OpmbiLVeRLuMzBm4HEFHDwMZ1h6LSVP-wB_spJPaMLTn3Q3JIHe-wGBYRWzU51RRYDqv4O_H12w5C1"
	testSignatureData       = "my magic data"
	testSignatureSignature1 = "EC5hZunmK3hOJZeov_XlNIXcwj5EsgX94lMd-tQJTNUO4NR6bCO7qQkKjEeFJmI2QFYXGY-iSf9WeMJ_brECAMyYAix-L8sZqcMPXD945QgkPsNQKyC0DX9FkgfSh6ZKkA-UvFSHrkn3QbeE9omk3-yXpqR-M8DlVqmp3mwdYlYRq0NdfTaD3AMXVA4aZTbW3OmhJoLJ8AxJ3w1oG5q_lk8dpW9vvqfIzsfPABme6sY5XyPmsjYaRDf9z4ZJgR-wTkG06_N_YzIklS5T2s_4FUKLz5gLMhsnVlNUpgZyRN9sXTAn9-zMJnCwAC8WRgykWnljPGDDJCjk-Xwsg7AOLQ"
	testSignatureSignature2 = "JbHSn1QEQeOEvzyt-LpawbQv4vPEEE05bWhjB2-MkoV-tyq9FykSqGqhP3ZFc1_FPrqguwEYrHibI2l5w3q8wnI1fcyRUoNuJxmBSzf2f_Uzn9ZoUSc7D9pTGSvK_hhZoL4YMc_VfbdEdnDuvHZNlZyaDPH9EbmUqyXjnXTEwRoK0fAU1rhlHvSZvnp0ctVBWSkaQsaU8dJTKDBtIQVP1D5Py2pKB2NBF_Ytz2thWt7iLjbTyjtis6DC-JKwjFBqv6nQf42sKalHQqWFuIvBCIfNUswEw4_sGfwWVSBBmFplf7FmD7sN8znUahYUPGCe1uFNly6WwpPJsm8VtiU80g"
	testSignatureSignature3 = "FeMZtDP-yuoNqK2HYw3JxTV9v7p8IoQEuRMtuHddafh4bq1ZOeEqg7g7Su6M3iq_kN9DZ_fVhuhuVcbZmNYPIvJ8oL5DE80KI3d1Qbs9mS8_X4Oq2TJpZgNfFG-z_LPRZSNRP9Q8sQhlAoSZHOSZkBFcYj1EuqEp6nSSSbX8Ji4Se-TfhIh3YFQkr-Ivk_3NmSXhDXUaW7CHo2rVm58QJ2cgSEuxzBH-Q8E8tGDCEmk4p3_iot9XY8RRN-_j0yi15etmXCUIKFbpDogtHdT8CyAEVHMYvsLqkLux9pzy3RdvNQmoPjol3wIm-H0wMtF_pMw4G2QLNev6he6xWeckxw"

	testApplyResult1 = "4888463523031960242433011351869933031323449643727040575267845889024687728335498778580107772380133477685774181643505931825934957930382325880471259986379481812500627973160053255661531371646409811509314633501243940664636646061820889680085814148846909166047015411072766645557150863726324686329555504988218300157350050244330800608990473857422956474907992645150135009641078679841383743592901610548809345334092249541224194617772261801029926867018380017174837064939222904135793934281777271768074365848986515969280223067040944794713036350956931528960095885138443276664224260998457842188266813037245274736142500125239194502844"
	testApplyResult2 = "4507231671370752505602755977590396112621674481083265860512309904190844081473672687113571201679100199249103736753050763319055928702852119196416376592720547548828221801243402864128135255910674338934597392942014067601560763773642475584288073277521204521238267770771818950526410076154941598183545650153560127448070571990601653356087553587449056140815997932967045981427419821913844385893045572995479437364617050357577443254958609447749174939815145953700633456010434315651154939638819682768929289926209763604603144006133189556004140338999730960179908317728822819073361427903811867836609178300474931337707773914834613166268"
	testApplyResult3 = "2336955630640787492959154171705648955339841630419984156572638628245093899798637966056353389240042265222529086025383166241367534300600405572378833658081662481081423098121333017620562491312743233639885193457468302381508024607931693189919377188652556384936630767256176111108085637531446970806885942692696671359617668575198489491391810559485934064895021311173873852167271682817593291847000486318561713794817890788850255243567478007109684545391556567999277533727108196717153437790827015123911382038146667157158320092927356268324058735310335473792133693529680520431950191425771709462002857497205750129196516387192225797564"

	testMgf1Bar50    = "382576a7841021cc28fc4c0948753fb8312090cea942ea4c4e735d10dc724b155f9f6069f289d61daca0cb814502ef04eae1"
	testMgf1Foo4     = "3bdaba83"
	testMgf1FooBar20 = "829e6d6ad38a624fa580a395b5166afbd2f36fbf"

	testPaddedMessage = "4a8a3925bbd3c2baf74f55e73254bf71224836fc484ff845d2c62cc5310b71385762d210d43717ba4534a50fa57c4bb0020717a2cfd03d4000d5ed4e195d278b5d5b5cbab097f15daf621afc776509f0c505be6b52c961525652aeb1e521cbc3c7cc882f8b8f869da591a3d19fd53fa9655b3eee065283ec5e04da3264e0afbc"
)

func TestRWPublicKeyFromString(t *testing.T) {
	pub, err := RWPublicKeyFromString(testPubKey)
	if err != nil {
		t.Fatal(err.Error())
	}

	if pub.N.BitLen() != 2048 {
		t.Fatal(errors.New("invalid pubkey length"))
	}
}

func TestRWPrivateKeyFromString(t *testing.T) {
	priv, err := RWPrivateKeyFromString(TvmKnifePrivateKey)
	if err != nil {
		t.Fatal(err.Error())
	}

	if priv.PubKey.N == nil {
		t.Fatal(errors.New("invalid public key"))
	}

	if priv.P == nil || priv.Q == nil || priv.IQMP == nil {
		t.Fatal(errors.New("invalid private key"))
	}

	if priv.DQ == nil || priv.DP == nil {
		t.Fatal(errors.New("invalid private key"))
	}

	if priv.TwoMQ == nil || priv.TwoMP == nil {
		t.Fatal(errors.New("invalid private key"))
	}
}

/*
	Check out the doc at
	https://en.wikipedia.org/wiki/Mask_generation_function
*/
func TestMgf1(t *testing.T) {
	data := mgf1([]byte("bar"), 50)
	enc := hex.EncodeToString(data)

	if strings.Compare(enc, testMgf1Bar50) != 0 {
		t.Fatal(errors.New("mgf1 test fail on string 'bar'"))
	}

	data = mgf1([]byte("foo"), 4)
	enc = hex.EncodeToString(data)
	if strings.Compare(enc, testMgf1Foo4) != 0 {
		t.Fatal(errors.New("mgf1 test fail on string 'foo'"))
	}

	data = mgf1([]byte("foo::bar"), 20)
	enc = hex.EncodeToString(data)

	if strings.Compare(enc, testMgf1FooBar20) != 0 {
		t.Fatal(errors.New("mgf1 test fail on string 'foo::bar'"))
	}
}

func TestRWPublicKey_internalApply1(t *testing.T) {
	pub, err := RWPublicKeyFromString(testSignaturePubKey)
	if err != nil {
		t.Fatal(err)
	}

	if pub.N == nil {
		t.Fatal(errors.New("something is wrong with pubkey encoding"))
	}

	signature, err := base64.RawURLEncoding.DecodeString(testSignatureSignature1)
	if err != nil {
		t.Fatal(err)
	}

	result, err := pub.internalApply(signature)
	if err != nil {
		t.Fatal(err)
	}

	text := result.Text(10)
	if strings.Compare(text, testApplyResult1) != 0 {
		t.Fatal(errors.New("apply result failed"))
	}
}

func TestRWPublicKey_internalApply2(t *testing.T) {
	pub, err := RWPublicKeyFromString(testSignaturePubKey)
	if err != nil {
		t.Fatal(err)
	}

	if pub.N == nil {
		t.Fatal(errors.New("something is wrong with pubkey encoding"))
	}

	signature, err := base64.RawURLEncoding.DecodeString(testSignatureSignature2)
	if err != nil {
		t.Fatal(err)
	}

	result, err := pub.internalApply(signature)
	if err != nil {
		t.Fatal(err)
	}

	text := result.Text(10)
	if strings.Compare(text, testApplyResult2) != 0 {
		t.Fatal(errors.New("apply result failed"))
	}
}

func TestRWPublicKey_internalApply3(t *testing.T) {
	pub, err := RWPublicKeyFromString(testSignaturePubKey)
	if err != nil {
		t.Fatal(err)
	}

	if pub.N == nil {
		t.Fatal(errors.New("something is wrong with pubkey encoding"))
	}

	signature, err := base64.RawURLEncoding.DecodeString(testSignatureSignature3)
	if err != nil {
		t.Fatal(err)
	}

	result, err := pub.internalApply(signature)
	if err != nil {
		t.Fatal(err)
	}

	text := result.Text(10)
	if strings.Compare(text, testApplyResult3) != 0 {
		t.Fatal(errors.New("apply result failed"))
	}
}

func TestRWPublicKey_Verify1(t *testing.T) {
	pub, err := RWPublicKeyFromString(testSignaturePubKey)
	if err != nil {
		t.Fatal(err)
	}

	if pub.N == nil {
		t.Fatal(errors.New("something is wrong with the pubkey encoding"))
	}

	signature, err := base64.RawURLEncoding.DecodeString(testSignatureSignature1)
	if err != nil {
		t.Fatal(err)
	}

	digest := sha256.Sum256([]byte(testSignatureData))

	result, err := pub.Verify(digest[:], signature)
	if err != nil {
		t.Fatal(err)
	}

	if !result {
		t.Fatal(errors.New("signature verification test failed"))
	}
}

func TestRWPublicKey_Verify2(t *testing.T) {
	pub, err := RWPublicKeyFromString(testSignaturePubKey)
	if err != nil {
		t.Fatal(err)
	}

	if pub.N == nil {
		t.Fatal(errors.New("something is wrong with the pubkey encoding"))
	}

	signature, err := base64.RawURLEncoding.DecodeString(testSignatureSignature2)
	if err != nil {
		t.Fatal(err)
	}

	digest := sha256.Sum256([]byte(testSignatureData))

	result, err := pub.Verify(digest[:], signature)
	if err != nil {
		t.Fatal(err)
	}

	if !result {
		t.Fatal(errors.New("signature verification test failed"))
	}
}

func TestRWPublicKey_Verify(t *testing.T) {
	pub, err := RWPublicKeyFromString(testSignaturePubKey)
	if err != nil {
		t.Fatal(err)
	}

	if pub.N == nil {
		t.Fatal(errors.New("something is wrong with the pubkey encoding"))
	}

	signature, err := base64.RawURLEncoding.DecodeString(testSignatureSignature3)
	if err != nil {
		t.Fatal(err)
	}

	digest := sha256.Sum256([]byte(testSignatureData))

	result, err := pub.Verify(digest[:], signature)
	if err != nil {
		t.Fatal(err)
	}

	if !result {
		t.Fatal(errors.New("signature verification test failed"))
	}
}

func TestTvmBadTicket(t *testing.T) {
	tickets := []string{
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:sfWmCIu1O9LuPHFWOiemo4RV6mnExuSDk46hzGtHZx_P1_QrLhOOhM6qWjZ8eLdYPlQDLIvW2RIxljNwsdyd-_qjJbKoulzLPLFCkORzEHVWoV0XU8I9pGt3JwnAdfo-Cqn-3QI8DzQa5vP7TcQYjSmi73md93AApqSp53nJyQ",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:hvjULVQwcpa00LpUu3SLTrsGj6njYcU6eTXBYTcdelWX-d8Gox6iQdqjPOf22Xejjbi14wM3LG9rnPp8ROFeVjx1gpJxSwjpZjh2UtmtkNCja4C-Lpwd3Hg9zONLTMJuzRuKYtH1L5iJdT5MGYJu-2NUbguWXWPeJLgCTRjBlg",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:H7FVTx8F7EkAcb7cFwLSgimH5FEj4FyXFAopZi1ceHLIRk8CfsGgRPORUcQfx7v3K1aCzV9pBxeTLM3TKS1tlK9mGjZaB8wOI5g9-E42wH8OdjnUUInUka1-XSTbkAg6ijYdeAEwh-RxeSZ8ENPqQ5UbIAls5X1tt3bOh0jFlg",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:objJL_ipPWtf9vSp_m4aBW1c09Iej8N6edv2AGMKMiMTueuftXX4JmlbKR5zNGOjUopN_01J3R9U1-dUonyVS1hVHsYfsZUirbeguDif45Ewf9MLUKkqGFWnZOjKgq7L1zsu8jojs3PRAtqde3We-v5dtBimjX32T8OMl2R07Q",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:Q-4GI2M_pQhHtwfNEUlcpNtpmIA2s38Bfzt4rZ9PNwzb0KS1N9BO9bgrocyb4v38qKAqw5hZwuYPu-bGS16oom2EskTdKb8L4mUGNvQ1Tw7tJ2p8WsLxxNXxFnc4MmAYkPFcEv_hkps2b5B8S27mxIYCA4ZefkNv6a-kDJ-Z3w",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:X8KCBaXXmO5ORWuW-ZYQtbHzsIbA6RmKX_DztneBRZP9IGo2F16qarpixuiz9Rz2vFUdpkHGmK5dBqWtEkFWs_wrYKdGJiLRY723SiTb36zVvH8_l90sPy4ih4RbTmb3MJyVfCQ0akGSEPOiMTgbgyR7NtxAbZUdqi32Q_xT4Q",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:ZFVMm6WGsJLtbb79pXAxspnv-4rgk5gKRD0Xq9pYoTMBsbuT6epclVO_Dd8A65HppvPLu4CYzwju700L88si890SmZN54vpaImdG7UI-zVmFS7Kl8V73y1E-jajA4VDOmXiLDy26SgbxYGwOwAXi_RqvJT73dMGLIHgFhCcG7A",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:rajJyEdbGyAGGbAsd9fF3IkjvjBf6n1sBb-XLl9xBPbWAjR3uKBqeg-9FbqFqof8ecSaXQF5IVhyoEkI-bJ-zuEFKIaMIFffoY-UEdGpyJL5CBLdnp_H8L3wM5DNLFrIi97QbUBN--0qtebM3b2eEuqvU2RjG6Y84oJh8G5cIw",
		"3:serv:CBAQ__________9_IggIlJEGEJWRBg:693CtnBWQenIH6K2y3dV4nHQU7UkMRM20x_LyyBQ6JVJo0_WXHGvRs9OARDFRDDHMLYX2RpDeko08cy98ywh8bB97eKcSdn-HeduK2qdmilURRaaZe89DESHLvBEUdlIOKvP87haUfaJr-ioF4F_lWb-hhEUGyFjoNQx6Zofmw",
	}

	priv, err := RWPrivateKeyFromString(TvmKnifePrivateKey)

	log.Println("N len ", priv.PubKey.N.BitLen())

	if err != nil {
		t.Fatal(err)
	}

	for num := range tickets {
		ticket := tickets[num]

		parts := strings.Split(ticket, ":")
		msg, err := base64.RawURLEncoding.DecodeString(parts[2])
		if err != nil {
			t.Fatal(err)
		}

		signature, err := base64.RawURLEncoding.DecodeString(parts[3])
		if err != nil {
			t.Fatal(err)
		}

		if _, err := priv.PubKey.VerifyMsg(string(msg), signature); err != nil {
			t.Fatal(err)
		}
	}
}

func TestRWPublicKey_AddMGF1Padding(t *testing.T) {
	priv, err := RWPrivateKeyFromString(TvmKnifePrivateKey)
	if err != nil {
		t.Fatal(err)
	}

	if priv.PubKey.N == nil {
		t.Fatal(errors.New("something went wrong with the public key encoding"))
	}

	msg := make([]byte, 32)

	for i := 0; i < 2048; i++ {
		if _, err := rand.Read(msg); err != nil {
			t.Fatal(err)
		}

		testDigest := sha256.Sum256(msg)
		padded, err := priv.PubKey.addPSSRPadding(testDigest[:])
		if err != nil {
			t.Fatal(err)
		}

		res, err := priv.PubKey.internalVerifyPSSR(testDigest[:], padded)
		if err != nil {
			t.Fatal(err)
		}

		if !res {
			t.Fatal(errors.New("failed to verify PSSR padding"))
		}
	}
}

func TestRWPrivateKey_SignCheck(t *testing.T) {
	rw, err := RWPrivateKeyFromString(TvmKnifePrivateKey)
	if err != nil {
		t.Fatal(errors.New("cannot deserialize private key"))
	}

	msg := []byte("test message")

	for i := 0; i < 4096; i++ {
		signature, err := rw.Sign(msg)
		if err != nil {
			t.Fatal(err.Error())
		}

		result, err := rw.PubKey.VerifyMsg(string(msg), signature)
		if err != nil {
			t.Fatal(err.Error())
		}

		if !result {
			t.Fatal(errors.New("sign/check test failed"))
		}
	}
}

func TestRWPrivateKey_signPaddedMessage(t *testing.T) {
	paddedDigest, err := hex.DecodeString(testPaddedMessage)
	if err != nil {
		t.Fatal(err.Error())
	}

	priv, err := RWPrivateKeyFromString(TvmKnifePrivateKey)
	if err != nil {
		t.Fatal(err.Error())
	}

	if _, err := priv.signPaddedDigest(paddedDigest); err != nil {
		t.Fatal(err.Error())
	}
}

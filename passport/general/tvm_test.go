package tvmapi

import (
	"errors"
	"net/http"
	"net/url"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

const (
	keysTestResponse    = `1:CpkBCpQBCIwQEAAahgEwgYMCgYBwNStrTLWcPHVecf7WbSrFGn3__GMQ9u2zTplXj5z8yd2VDvKYc2rqXJWIKXgxJ4pPnKtWF6DDaJGfbN3nxpTZcEuQLKqKvy6groHpvLIUhccm-5vFJka5vZ7I6BPZkqJxjoSOQUnS7ZRBLcpFkagKU4buvxdXDa0maD7wP5WgdSCeoJPQBRAACpoBCpUBCJYQEAAahwEwgYQCgYEAklyWlCB0ivS9HZFukNKAQ6zD9QlUk3Ocv94VsgajH0hfqVwOSY3uMxcpjsNWv_O7wKSm4Y9Eyb8lfkikntyXiz3SQluzI6gkeiBHGZlKBhXxgmsdNtc3hB7ahCbKevUk5y38CyYn8xpC7I_Wb5ApODsL7N3buhanU8IRttR2SNUgnsOY0AUQAAqZAQqUAQicEBAAGoYBMIGDAoGAfBJS1moHzBRhx8syfl8VtvLJFVfS1dPyzk3xuBHprKsuNPSP4YsiSHwIYKOdPqZMFB-kJ2vLHlcmj03w-vePtrC9JHRIcsH0pv_Zwk4T77wczaM2f85LMMdzUVpjEn_-3W0lckcfx-E-stCYhUlRGtN8dJSZU0ruRB1XNdT8bLUgnuad0AUQAAqaAQqVAQiiEBAAGocBMIGEAoGBAI29dc3uUnVxB7Z5Lrh0TKghF6gFeGmcB2ijKHMn-IdVCm3AWqklW_Cc8nMGChey9PwkeiQmPn_4paesH9k3L9EryXBkinNEC3ZZ3uMRPOFtjP-C1aMRD8qcG3n8Fffx8QoCE0Xd_tiKg8GS9LRr5rq_M8QgneBA6aEgrWBJHpIVIJ6Jo9AFEAAKmgEKlQEIsRAQABqHATCBhAKBgQC23i44Jak-IfZvZdJQ5vUq8Ok2oU6id9UTBUOgS2X1AB-oDu5TjMFdYlhQyWelNRP8ewzl55qNBTmJoV2tZdTi0TrhfaWuOs8XdUGdr_T7feETUCizfIsKBg3tgZgMR9CPZah6wGUwRCwmzTvhQcwa3arBh-Z4m8KzvpPxXitatSCerKjQBRAACpkBCpQBCLcQEAAahgEwgYMCgYBunqg3Wiu1c2s9qq1DveX-Uh3wg5MGl46J4hQLNGcakto9_nd1Bxij_RwL6XiaiJej2NDComc9AtfZTqojtRjIp6OK8y7iT-bbkpID_iSSMKbtjfHvWds2k1eijbu8KnXiR897NdBepctEpfxFJqYZ2_XU4H_Fz7A5gzclruQ-bSCez63QBRAACpoBCpUBCMQQEAAahwEwgYQCgYEA5irhdSHrpIfLOZKjOE96Yt58eLjv7YGC7-buH0utLBvYXolQkC0x9JewfLhCfxdBDLFwRpbk7OjAJMiyi3mC0vIfbzbFskL4Ww1IAyGioa5J5i5FoJ0rBjmiItxqfz9ntRQnblxgs8AJkAWpeKEODycXHB7lFLYRhRLq3qaqS_0gnvKy0AUQAAqaAQqVAQjMEBAAGocBMIGEAoGBAKQp1rlwAwHIEax_FOpe5qhIR4fPnAfTigLzsLhOk6heeRf4c1z9cntZ7FYzx02V0pk2-pfJHMeuoFPytQMxkyLE8BES4J18gMcvHneyNCg_yZ5VZa7uAqVPCqfOyxpn_-FuLjiPSBHGwGcYMVh9Yl4nkMSje99BrxkB767Opx-NIJ6VuNAFEAAKmQEKlAEI0xAQABqGATCBgwKBgHUj14mZpp-yLjkc6kowJY-eNZqHIGrh0h4Am11mG1_TnXKkACy5h12ARaYycqqUymwKARR90nVNkpVlMdaRyfToDk6Us77h91j2I6E3blzfyBQogWts4IdXqZeuKJsU-8V8QCtajvh9_4HmF-fuXjOXpMBCceyLycm1GIcsgvDVIJ64vdAFEAAKmgEKlQEI2RAQABqHATCBhAKBgQCdgr6okQR61GA_IxZ44mMSBuzR3moAC7ucFwX15u9PQURdMgavIJk99lb3BXfvwgO64jAOahVYGS7DzqlywfsAqUzOtJjFA-oXsUIYFM3kgIEuIBEyFhQJWcBxxeklz_17p3JAiF5u_ft6EK2QpqhkK4h967x2F1GdVPIHkGYbzSCe28LQBRAACpoBCpUBCN8QEAAahwEwgYQCgYEAlTrPsKmgZtk5TujD2Tm_Oqi4Dt0YFdfbxGDpLKLfSFw7BMFw4-58TG3jflJCQsUcxSdb5lkj6TbSrWJQ3aSr9SFywA57nVJsF957Ud92W5VZEGbqCW17LcYVmdKjoRq6o_eHzLfVlvjnZyM6MRSrgoju1ML_uZJ27YqcrMgUvv0gnv7H0AUQAAqZAQqUAQjnEBAAGoYBMIGDAoGAcjTJLJ8Trg9IOKwPAapbH56qXciDmVcGFx9V2iWsCTqhH0sEMHvuFQF2nVad_cGV42ejf8oEGKPTbuCHq-Qi8hm4PCR9AC2pTDW-QOedTJZt6gOtysyon28NxifyFm9AdfOGD0Ur3YA2Su0H3iCXUr_BqIfEG673X1eoiPSl1NUgnqHN0AUQAAqZAQqUAQjtEBAAGoYBMIGDAoGATKFZ_OjG4kMJIskjbJeso0_FACYTbts_ULBN1KP3SlRM2P-fqBwW36IPWMz1AfE80Wls9HJfBwk2gtfD1I_tuGMwKcpZ0fT4oqBm6pthjbBq6E00x2jac98Odcm6d2v_qTPh7iSPyvi5oBMjSJdsbP3dc6hTUBc-fItkCpf6PG0gnsTS0AUQAAqZAQqUAQiAERAAGoYBMIGDAoGAU3pTjs4wIpMdOjMJJsYpQAD6ia_PSAMsF3KE99qZXvzgkF9oALSA5839Fcxb_zEBnh766-G_8hMR_u5xprnGzCWDjR7L6gf3OxQGm1ZeOlz2RBWajQX6DrWV_A6opN5heDnPSVsorBPpt9YrTwhhzOxe5PNaSBRborZxFgW7pUUgnufX0AUQAAqaAQqVAQiNEBAAGocBMIGEAoGBAKuXh1HddIEfzZkuCCxNb4X86yYaSs93poJpZhd3hceLxa2Rg56GiZuXgy6KTIB6VriCn2eRL01q790kRoMYHY-Jh-60MseX-W8aYNcGC2nQOqTp3j5Agp40IQ1SlEi8NnQOc6sJ4e2q5IVeVasuBRB1tiXBorNQpRPO1oJ1OWuNIJ6gk9AFEAIKmgEKlQEIlxAQABqHATCBhAKBgQCJ2K4qcqCxyXt6Psrec9Cyso2CCj0lNwzhXT4WxLPRbNGI3KIVJACKO0hhVcKT8LY38apnDvq7LR2l0fhrIqXOpZ9OagLXymFR2aLng-pXeZ1FymB32n80gFA8xYDkS_tqbDJYp25WNE3tDQs3NiURuhkfOOdUmvNVVu8OGCZxHSCew5jQBRACCpoBCpUBCJ0QEAAahwEwgYQCgYEAs7iDb837VkX6Y7Ng1cj9hy3XIFy85nGNCN0GyuH-81l4wxJ7lm_VPNpmXZP2and1vy5rDZZK7-hsuyw36NQ1qSCuLAJ8xcMarTnfzqtLO6yVH8vAD0m6mEBGFxc53S5bQblaD9IN1VEOa3vNsKqsEbjjEnMwruEwwimIHOYP2gUgn-ad0AUQAgqaAQqVAQijEBAAGocBMIGEAoGBAL8ZGYKOmBhtXJgjHxdk8xY89teap336bEktMx5naOxoojHkv4ueViEHqcmAmBV7fLKQTpaHV34g53oDAgO-9YXfRT4CFoo4QKY_GEmrnJXzZrx_aBwjbLuXxpfcnthtx2WP-5rwy-Uzst41921IEly0Eb3x5mVko-58OjdB5RVFIJ6Jo9AFEAIKmQEKlAEIshAQABqGATCBgwKBgHn-waUYOTYeu-ImIePJFM0x3nsWrigmjnWlJIM1DoqL3GeKEzhaMQyeuZbcOohGcvy9Erp38CaTvTxglrxBPzTJ4ztJQ5h5loGibqzDMGum6cTR1mw2eqdKEkK0I7Xt05KJodRS2wf0yHe7XRFcOAx9MkMf_CLn-6fLnydKdIvNIJ6sqNAFEAIKmgEKlQEIuBAQABqHATCBhAKBgQCvM99t88QqjZfOKVGRkG6lzHhBgiOy8fyBU5KadXFPNBtvRcWTlnH3m78zetKsvWAX-WrDOXumtmi1WBHcFed7Mr3i3qF_BggSdx_WaNuxsDqjZFRUqXtexUqsMNyDsj1LzsR7HBccCRXy-eCWitxKWyk1ec66N1rR3_YTHdJ9vSCez63QBRACCpoBCpUBCMUQEAAahwEwgYQCgYEAldSiX58zT2in3WyUb7I_gl_3HsjmW86Pp1611I6gChTJfn2LfmuLfXazUnZF2An9ZXadmnQhp7tOwrfe8MeHgG0LE8ZdEN96EC1iVOrZkCyad_v5F2wH1tmLWIW8VE4_t5dOKyIbbtbps32I7QBj6zBktpUsE9GjtmZix2BdKqUgnvKy0AUQAgqaAQqVAQjNEBAAGocBMIGEAoGBALsU3oDPpUpU2IweAK7XmHSsbnjs3OjrmGS140A80MkED-BN01T9Ekt5zujPVSKltIJNGVYCjYHFbMJPtdVCMYK6TTOkpasDJtjrIRQKPW64CM_UpMslp-x7swVjKaQJgp7x3KK7avdeArXUSwHmMRv4kb4i-FRRO7vztyyC0_j9IJ6VuNAFEAIKmQEKlAEI1BAQABqGATCBgwKBgFNRCDy_4yH6Cln3oS7SYK9jkV1UMSsEka4j2u27AfXXRMxyRq0Xh6PU3Z7-SyOEE3nBXgcX2ZApoZUPqS0HIgIZ375_L4yX6iYbnRqaN_nzQlgru6AhyIA13D4tt9FFwSMtVUkPLXQGeReARyp1WyLSs-bHDCl0zTX7yz5cOzZtIJ64vdAFEAIKmgEKlQEI2hAQABqHATCBhAKBgQDaKxG6COuDzNSK5UX_Huj0LIq_sRGAij5IUVk5-exw_NPsles5uYgWnE8piKsD27wUbYaUhSZTqdel68LXwKZLXTI2Ub9bJ3_-nX0E9w0qtTn8p09m1VbB-8V4NiSornI0mOVDyLgC3IvZc8mv6U8e13r6T9Yewtfn11MoKa8NVSCe28LQBRACCpoBCpUBCOAQEAAahwEwgYQCgYEAqwK1DSr43nSXEJXLLUZJDn6i6LZMh3AAalAk3ZNCLA8mKX1hpqb10M018OPluKvWpxqhLfHGz8zu_ZScGIdTMtTUDJYlG4naRRJhiGeN0gk5iCBYzGp1uI3tlUDBegnh3wN-EQrUIA_wWzRGdhf499tpuWsgKtBtgr77mBNiEk0gnv7H0AUQAgqaAQqVAQjoEBAAGocBMIGEAoGBAIOjS8rw00ugpm9oUsAzY2ialgVlMseXGe9v4HLnaKDTbxSFZhBTm2yjeiTocpe7Ey49l2h_w8QBiftpkHtrsufaHwhu62U24QANNDM7gqQNGZnikWm_ht4JQq6q5KBSx6ukgrQQH0_kscjwH7XoIuIUCPiLul4PId3x7G0gzGxNIJ6hzdAFEAIKmgEKlQEI7hAQABqHATCBhAKBgQCrHzvsWwKR5Qz7yh_sQSvnn-GDRYliQz0tHDX2UfCDjIBn1spVA3xVGEVhOKJBVxyDyytFMLvOnJjIc5z2RZY_ikwSQoTJhZW4yIvaJ9qQTrPliovbRMkbRzZp2wWKhv5xGtIix9cWht70VKhVJbPEpv5j2k0BiRPFktCfngfetSCexNLQBRACCpoBCpUBCIEREAAahwEwgYQCgYEAkw0lcml6BnSD4GavTSyBcwhHffUURppy2LN6-49RfFUf2vvcVbo_X4_1B7UdmxJp4zq8sS7UGaQhOuSiVHXRJk_ylbHXYgDZQ7fAmzs8kN0X2FpwIwA67iMeZjHIIuR_Sua49TDLBb6F0vUZfqmNHwvIGhjwKT73kNNo9qC6TG0gnufX0AUQAgqZAQqUAQiOEBAAGoYBMIGDAoGAeyxvz9hCspZQ7CWR2Fx6mOELzBGHj3qpm5arY5leYcAMVPLzb2UkKLXdApIfrztXW6pmqMp7oZCy4BHiL2_xjgIoVwQTquNE-9qvcldBKzMXddkH0Z1k_WKaUrfI9CO_HLjxHLXwwdlEyZWGCg44fJXA2ZcU48bwIEtMfVTQYn0gnqCT0AUQAQqaAQqVAQiYEBAAGocBMIGEAoGBAIXFNYG-yu2X1mcpchqhgnM4IUHQfiIBu4S3aIKE9SIz3D5G8ygfzoPwicFtY-wEbr1oS2f3NJHv4AUJRP2joYMxAzF6uU4V8HRut-OImYJNDel-VPkuGHcT__3tLJZ5CwkypSuqi7mJU85JHHIRekCBdDN8xiDAnxoXaybiCvldIJ7DmNAFEAEKmgEKlQEInhAQABqHATCBhAKBgQC0qp2ejfUeLhFP0eMk4VFVxTesWZB99-H3XiWSMocMxM0WdUaxDqSd_4PFsyd9-RTrML_CQFNmbQ04J5YPchXgwUYrDq08Y_W_qeSwv-sknc860fau3jB7KyL9EFYWowKpKyVyOvEcz9mF_NyJqs_AvR91bD3AvvvgwSmUroEzzSCf5p3QBRABCpoBCpUBCKQQEAAahwEwgYQCgYEAqD82nK567ZP2NBxxMWjOmQrSMaRCuqCUQpfCqTJy_PCxKKk09cvW4FMMHCzDlK-CzjK84byV3I54KflgwJeQvpGAIoQeBBk9ziFDUQWSmfycelCSWaQhhHDMxyA6tg4nft2SIirj5xEf-eoIROOVL_2brQFQEKU9x6f29U0jUMUgnomj0AUQAQqaAQqVAQizEBAAGocBMIGEAoGBAL8xqGT38hY8-obRZ-nozDmXPUaiKe8S9bpuI0hlvcOsPfoFuR7xtoDd_JUl1kJKcf8t8IiCDltmu5rI7ECnKKr-gTEw8JFWs-nIt7DSv6PA2GU2HLXOdPDhSIINTsUMoF-f2X4tox1RE0HdMhltnGy-IJ_9egjQz9gOuYgX4lhNIJ-sqNAFEAEKmQEKlAEIuRAQABqGATCBgwKBgGmiswu0kRY2wLb_cpv5z8ft3hPHyaKAsic-dd0gNUHcyIxhXBkWoru0Ug_C_Xqgf4u0OBPArivlBocNQATEsm5Id5UTuWA8KykISC3dgRMfIJmVeN2LYeonUWG6mbs-3dw1rtMuLcQddqPkCXrIKHCCprlFXFumA4dP82HYSCl9IJ7PrdAFEAEKmgEKlQEIxhAQABqHATCBhAKBgQDN1RqjsLkbOmyZX0rVZCbpd3a1Z4EkF0hOm5bjyuS97E50KOWP2Mi9t6SaVGZ7WpGcjW3yehGJVeUA7XjwnjiDCotCT2bMKtO4H4UIh7lgOiBIlGoZfh9K7DdFE4xfN_Vdy-wOWakPK3UpemXSk9Kxo-eYRbvO268xXv03JmkQ9SCe8rLQBRABCpkBCpQBCM4QEAAahgEwgYMCgYB3M5M906UeAwAzF3XIkvyMnOvALKEP0eeA0CDW-BtjJ6XL-EgjFEub8jm-0OrJhMCkumgUsazZQYMxZDtBG5M4EYMu2mH5E5XRpVqnDfuWspLipq-JhY5i7hhMeJefbtINBsnqS0dE4R8IvekmLCTqPqg--jc5AUjItsirRi0PLSCelbjQBRABCpoBCpUBCNUQEAAahwEwgYQCgYEAhTpMVxziZGDYGn1WJY-eYOIKaLl53TlPs9AlANqTCX6nOkusMpU8aoJRQ-3JS-CjoHQqg-g0k-vDE87g2VovVq1aVzJbaxM0s-lv1d9LgSNDgFV17yAIKfgCuhJDc-mDZFSP6ztRkWaYesvZ6Vy27jnf0Aw990dv5n9vbiSjil0gnri90AUQAQqZAQqUAQjbEBAAGoYBMIGDAoGAddvSefpJWZYjoBN0ny7TItD0HoDftVwIGECaNm9Nba3QOBeuaHgVgAFGiKTwmx6GztvTpEbcXfKb91yiLnPOtUfDvo7zumb-nmvhI_ZXK2XRRH8Q9MDo5O_L7ks7wgmH1b9Nynyw5TPXjwzIcEYPSrWZzeSE_PFuGFUBM0pu8s0gntvC0AUQAQqaAQqVAQjhEBAAGocBMIGEAoGBAKn0TEy7oJeQO_rAXM592DMT1VW69h4unIIDj7pTNghPfLcN5rfW9U3FTU2Pjsq137HzCNDXbQcbGk3H5iH8-fHFT6fVZhDpaqyYUZq89vqNX6lodqugyVlicO3AOF1KrbC5S4yaAZSeUwDu8n75e8_e1Pb_rJNyD_6EiwwG2jiFIJ7-x9AFEAEKmQEKlAEI6RAQABqGATCBgwKBgH5uUkK5rekJpB7hh9HEhEBCWFdAGMVGRvSoMEzRf5r4Mlc4VXf6dbW1QqvnpqwpTP_Y_6AxBljuNBv_ynCtm7A2ikIDGaz33Wdi2oNr4lXJIZjsfxRv5bzT8tWdDG6WSBeuglvbFrzHoCYlitynZjbBVX1A-Xdl2xUuC9D-7uT9IJ6hzdAFEAEKmgEKlQEI7xAQABqHATCBhAKBgQCJ2oy-Knvv-J4qYoh-_Pla4I1wSMIgezP3D4zV9d7oTitp2yrmLe7C8fVOJ8-Q3GLZ3snyTBTVeIp6GxcRXcsRDSYuPoF8kURMw2k3aGI0mWaA909zeK-XmZ7u1W0T751QekfujN4nDoovBSbAZu4KeqkGBhuY3pHjDDT7bqLxNSCexNLQBRABCpkBCpQBCIIREAAahgEwgYMCgYB4t_ZrTMs_B1AENNHNhFx1qbxwaEyFZ3sjTUEPUkXNsrYz5ekTUjxz1vTgdxv2o_IHipO-MNAbMVQzZeFXoS17nkqctJR1zxMYcJ7o-gMPxkCLPSczOe1UN9dBG0NpILQ-7kS_HC69H9BFzepSmYY9o7sf4lL55ffuZ0qA7aoHRSCe59fQBRABCpkBCpQBCI8QEAAahgEwgYMCgYB4c51zCQ0EJ_UoSvE9RRExT-8gB_XSbuPSP7V8qTOO5s2_84rF-dM82AMN3EAUNsStEd21bntkPsbTCWXkADkv08Xd8ygHD0x9teDpJOEYQ-OjlzmT2YfSGYOIuiztayvAXJAdXb85D1g_4a8iDURv-wXo6XmRlYJ9tCvEniPndSCeoJPQBRADCpkBCpQBCJkQEAAahgEwgYMCgYBTUyEBO08kLnBluN_PDSQs27L2g5sFfq_KeoIJmAGk6Xbb0U2DJo8xYIBaoC1aRgwhDakfTIzsfsMrUsXER5KZUax_h4_RDbG6Fvm6E21gMCa8sJRaerjkMowjlmsNwS4zmTRAUT87RxnFOuPSkOk4m6iHIB4rv0G54ZpPUOAoNSCew5jQBRADCpkBCpQBCJ8QEAAahgEwgYMCgYBfrEpi9YN5kdM1bmEzykzweHBaPXgTgIAKTvrJStmFpjw25HGd0tOf4zlZTQAl7IWnOGGr1eZvUVa_B8pTPmvQNzwZHj1aI5JbiuFgySyl5ubU0yyNZVW6ARpqH36Ic0xLcLtMUEmIWrd_Ha5no7WptK5YqrMU4SQFNXLAPg8SPSCg5p3QBRADCpkBCpQBCKUQEAAahgEwgYMCgYBz0DIMpqcBIhhO0UiceUVFZTo303splP6tP7KLwPyMG6ycK1Ua1F4Kse9EDhV8TU1NYjse7nn-SdkbKjRon0hMC1v0-dW8fUI5dPDDvTaWy_t6rRQipYceFCsx1-RwRWNSL8kKgufCoadpnW5htlJmx6MTnxER_ScoiatjhpgkfSCfiaPQBRADCpoBCpUBCLQQEAAahwEwgYQCgYEAoJkanFI_6gwb_FGOsj87llKpJVe_2Ubafcyb1BGbAsU_YAB1rICZZ6g22PgEY7Q4BamvU8i6Z0NpdgDPrhG_W6p9BfiwbCV4e3mwvNFR3FEMqaMofSt3PFgsDWaOhIuCFCLb97rdoQ0Dbh2VbWwTGpJwXz1fGO_NFjRmXKKUPzUgn6yo0AUQAwqZAQqUAQi6EBAAGoYBMIGDAoGAaoDOK4NIW74eghx9C2iXmjrASt4LCjW_z8kiZrCVqYEPJNsmS5nBNE-PEsrb3OVkzzXjRCyFPOw2ujS0RgX45MxVqa-MZvKML3jWkDYUMaUM4Y7GevoXqaNE-3tCiahik7tWuMQ2Wn9WtQGCAeqDzdGZKw6tTIO_glP0_PJcOFUgns-t0AUQAwqaAQqVAQjHEBAAGocBMIGEAoGBAJKbBI92_GPGTYvnnxBFmZVZN2NcVvR6sGf8aToM55rPdPJ1n545KcjL5bASkNid7TMKLvG8v-K7RRlFh-r7KD2Y2UK_JE0USEWlWfXv6k_z29OWP8yUaDVjWyaNShKVwCQv2bgnsZR1_EjdzgFOFHJn_iBbC8bswzulfejbP6b1IJ7ystAFEAMKmgEKlQEIzxAQABqHATCBhAKBgQCRr7AnVls5NnuxSQZbic05FYsEYC8Sq4XQtTnIe5KEhOflUMks7LEB8LTKlXXNI0qClI4nHzEDayPuu0tAorIdrdI5lvuGuwcTyxCFblgirROrhgsYDD8ExlUsqrt67CjO44PC5paY9jvsvQik83kdJuw-2i5M6Pt4xlk-HMw1pSCflbjQBRADCpoBCpUBCNYQEAAahwEwgYQCgYEApny2SjUFWZzSFjUMlcZCSgbJpHVg3GyS6FwQQvO_aSntm7e4dfXLjoAmAB-BjzoFFM_novYobwEJqjILuIqjlTLPixTwZ4PMECjiWURIg1UlHPNA4n6sRImAzpYA-82nGg_iPfvxRyq6Bh5vvP7T1GXUYinXKxhTT2RJU_I0_c0gn7i90AUQAwqZAQqUAQjcEBAAGoYBMIGDAoGAaBl82PREhgGdZMo6lmY3l4oZ13Rj3LJkdzavMzv0D0LIusvDCL9WAQ61Yd9_ARozINCK-lraD7TqtYFLIi2FQFPkOBAh2XSaEPttg6kWSr-7qMS1kowlA1KNvI7LbFPgc35uhXg06njXJJ2kd_XgAdTtDbn48qPB-m0ji1TCZjUgn9vC0AUQAwqaAQqVAQjiEBAAGocBMIGEAoGBAKB8YAN7zbA8Le1OyycoQM-e61Ga3zIT6tKrmP08WP4t6xykP1zK6xUf-eOO4zJXruR3B_EJiDtlEtgFVtAWdb4lngcYNY5Q-cozQPng3hJwfWyVsF2ECPtBbW4Hzo7nWKXE4EvfgKbv_Kl9Z7ZJxe8qGff2rDeI66wCWFcBsSu9IJ_-x9AFEAMKmQEKlAEI6hAQABqGATCBgwKBgHyHcPr7fZf60nfx36PaHmMnQb9uz-18Qi4ArFstRAv4lK2vSMy4IbJkH1B-fZ2sttrf3aaP9AjDLqIm1ZXU1ERcZWAkhfKvozAbZyxPi1S4sx7BA57Y-uCMRxbwy3QEK_UJi93PeSS5OfrbPbiJeNcebI3wgPcq1svED4PLqdNVIJ-hzdAFEAMKmgEKlQEI8BAQABqHATCBhAKBgQCP01wQnKxiI1bE9uBDiRaPeLe2Yh-FlxuXO8MpgylcUC5s1RCciELNyYl0oqsNyAZRblHY1fiOvX7ql18R_1E_MNFxtIlGUgYw0fiE_bYCxCsAJAX58I6k3W2NfF73uBzIdkD44ABLMvJjp5KUVAN4qDUMBB25d69RkkCClVs6vSCfxNLQBRADCpoBCpUBCIMREAAahwEwgYQCgYEAlOsPcNytro8NafRcEKCrku0PKqaeykXX0nkMxkUP9Fammk_ZZLAxzNN9_OJqxzPZGgbC05btYIaU5EEFXfHSPk5sfbSSyFaK2H8TTGhId2Hv7FTkr3laLtoQau2LcD9xouBQG16y44PqHJ_88IVU_B-SYM8sIY5vWsNKXIsBPgUgn-fX0AUQAwqaAQqVAQiQEBAAGocBMIGEAoGBAJmUIL8dsKj-e6bpNKeOWZ90CKuz5r4Ur6ha6AHLrOmW6EaqdznRyx_n5BJKxi0UkSVKrgz12RzpVexUy7qGHrHvxLOkiB5DRycS8HwDm5mmRC6NFVjsg8Bc-Y60tRglut7K9tLGE8Sy93gbt9NCfVImehSvQGNWBbznHr0-QVFVIJ-gk9AFEAQKmgEKlQEImhAQABqHATCBhAKBgQCR7NOPsKHA_Grpnc5oGnpGBfjxkgUWcC5WQNxUp2v58GV0_5EiqHeH4_kdl6BVFNhIoRbWHZ5SU0fObpwMNiIa2qYdYGI4jyqDlxtQA2Vdx7P6I-LCrWk1lKKdNPPt3KB1mo9B9s-IO1_8QXcjq6vI54DxETc9e1hAv7qUeL4nhSCew5jQBRAECpkBCpQBCKAQEAAahgEwgYMCgYBU3MnW3sr3wvsxTooyc8MFgF1vxwfzdZsaPcUj0GCkIXk77cumVhjKb-WYa2ZTXFQhcXfcn9c0gTFQfNVv2x4t4yeYiN58HlozwbnGdaAYkPd0kNyYe5RyRO0uiO-2KwG8LHTytG4719CnpJ7LvphKWcPkBOOKEG6QHh02vmPNRSCg5p3QBRAECpoBCpUBCKYQEAAahwEwgYQCgYEAlA1W3BWVkpkE2_E-xaiSyR8NRD5k33vfr7KEgXVQivD7i_9qEQGEfbyeKcT3z3fxmjeEB7N3lluQGYtINoXKX2cws309xHjO8-r7SOjBW83fsu3n2V3lg3Xp7mkQae8Siy_TBixK6femn7b9HY7drqBH6P3h9ICID6Ef_se41_0gn4mj0AUQBAqZAQqUAQi1EBAAGoYBMIGDAoGAXMeqO81P40Sq49miEYQk_XITf5bwFEqSUO902HgLtHSvLvzNy_iWPox_fKjNj2nFymE2LQobKQ_eYNkQ8meW-Gxju5uJ9dxSv_CHoBhe8w9W0qvCqiHrRNB9a7U-GVDhgx0HC-A8basd-v_VWN4rucPHa-porf634NGXqhWhkQ0gn6yo0AUQBAqZAQqUAQi7EBAAGoYBMIGDAoGAfvMN-TzczNzcH4MzSypqXZFCcNAR693otttab71AY4neV9OK9Dh3Dy4rhCoI1hPeA0HAd-kPlfCHPmHOh0xo9_d0myAqkNql4IbYp7mBcUOcYCnFFAghEu2LSY2F3VWEL8G7CTnvkJ_LMGAHi4JaVObZNzNJYxfyKIZzOhMTjb0gn8-t0AUQBAqaAQqVAQjIEBAAGocBMIGEAoGBAP8TMs47jmyv_RMefEeZIc6vDiLZ1x3HVZ05FKCqVuFr2vcDPpOh-VqGwY_M1m4RkuSAstxKHXnMzkPND2sZJ2QL30ug3EHl_B05TLcZgez5Z0VKLMs_52_d3wpYRJj7KkjzakxdxCsQJcHsAp0yjrJ3WUXUIhN2NqPTQlpDxovdIJ_ystAFEAQKmgEKlQEI0BAQABqHATCBhAKBgQDejK781KjOqU9agPqQnevcEQP8Zz4jUSSTGLxrZTjcjoeJEQmBJ44iRKWGADJTEFW_jdp8WPR_4QkGxu6bHSJ7eYnIyQMUm6oeQ55XGSQzjcfWklC0VxJY2QpHMbUV8MbhwsEnbBxlgUEWLri6QxgoaJSlsK50aNv-teuk0sEcfSCflbjQBRAECpoBCpUBCNcQEAAahwEwgYQCgYEA07B1mv9iGtu4m_IvpEICVX_f_61QKtabedos_1yRFhKI9ESLSFTEfB9Ek6zXphlP7t1qop5SdFsH6zgQKnNMF0Nve3VFhV9sGuKlXapoUtAFCUud97i9nSLiAXOjFL7Gdv-QixFvjOLa8SqML9Hp70ENf7-s3JVUr6qiBOhuBn0gn7i90AUQBAqaAQqVAQjdEBAAGocBMIGEAoGBALnLwDfpzpnnCg2jjBy4H_mU_DEerwfeSc0eDuR12VDh00z2ZrLqTS06Iy-E23mfvjErPE2OjQckfKhICJGTlUkiU5HazgwIg5PvOoZ-8hYTRf6-EkyD12XnfU2u4lOGDn-MpbLSiEFM922iJkIfC3IJkjvM4YEd8QuaWIOhBnSNIJ_bwtAFEAQKmgEKlQEI4xAQABqHATCBhAKBgQCK1EAhvqYdkAWe6BhCmSgjLu3iM5HK_Cy2Rtpcew7KosBCpf1U0XkAi0Gu3RRY35Ol64klAJ7xwNA1arY8jnSkdPjIU2KedYBL6SPawdO-mRpZyvi1EOC12bI93bW8fy51Sa3HFC5SZAUMuUgsk4HiBhs30MdS7JAb9zusTR8ilSCf_sfQBRAECpoBCpUBCOsQEAAahwEwgYQCgYEAhZwykSKE3qy10wDu8SZjAFj6LnNRBm8FDO6wipeVSKS77M85Y8Nw8N95UDAYmQe7CLrz5a3GIRpUV_ZmnxljXWpCzYU6fd2gcZvamjrLsZTma3k3rbD9R9lg9uZXlRY0mJmqglxQaqBah-2SnphUBukT9-CjvyFJyZ-CBfgY3FUgn6HN0AUQBAqaAQqVAQjxEBAAGocBMIGEAoGBAL5pftdwxrPfx_hvFY2FvY32C4T3P9Hq6um3WVLHr-v-3MLMq0hrkfEdEVQwTjza2eA6xtvTvcbjwOYG84m4ERqtRfstHNHYmDpMcR0__pp9bBVZ_Nq5MjGYaPgNY21Rkl9SE-WkvVHyuyxulYCtKvAGPwq7M-p0oFPC0MIdGBSlIJ_E0tAFEAQKmQEKlAEIhBEQABqGATCBgwKBgH0M79RWlfU6AFPRUko0Ok5fao2bHWvt_xaJLnpKc-gMK3hLt8q3vN0V6rJQ3t5Cq7NtXa91klc9fJEvLY_bvuoYgf5yLSAjV8188zyhrsHp4O5X3_IfUTUwNUtetuhoGcI7WVccjKA-NP8fzsdU5cG0D2assSQztDeMcvkta4tdIJ_n19AFEAQSmAEKlQEIkRAQABqHATCBhAKBgQCirXLHOSR_oLGVQeMyEmCXZZdguGe0xLotm0TcZg2QF1KVlBFX38UE6v-etf6EGf2dzZmBJz6Y0_az7ueUvHjEOhbcdiwnHvR2eLisa6ZbWikLILidz0knp5VbxAX41e9Lp9sfDyg48kzhhjb5F2Xx60MF_NFvE0n1oswEAmaQDSCfoJPQBRKYAQqVAQibEBAAGocBMIGEAoGBANPMJtJw8VTyJY5OvbZzn5AIq8qYqgRW0uRMs5uanjvq5PMe8JWjX_YRg79MqObAmGAqPTrbgUEDqO5yXkXGWd4HNzGXDGRrvdcXX1XSuiuCci4CpV3yPHIkUP1FLKRYeDIMz3RMVyw9lwI32rGKp45fuNR2Ay-j4lL7HDrehrDtIJ_DmNAFEpcBCpQBCKEQEAAahgEwgYMCgYBTNBVkrnoY510Re-BCsPJnZDXS0jru2hYwhAEJJlzMN3TznAEyfyD6v1v7l76zPzZ5MWWbeXTWDjQh17M7sqjLWTjX91x6m7Vl0kqraEBm0NSFKqKTQHZBkp4w5gf_5Uzrcv4_EHqJnOhEPwwBH5mGNhzKbU5AN0BnEnCzjCknFSCh5p3QBRKYAQqVAQinEBAAGocBMIGEAoGBAIn8DvqMxvIAPSzml4XMYZAA6jT5u6uewWq2VuihHtOlTO8p9jFENbwsuK3vunv0PFVxmZEQa5IisYvLJci7FwTWplmsfWza43IZcozCxzUjEGOOmoI6-VsOx8ByT_QsoVY-jBos8o8_c1kSKy_CA4xPjRFB9keCoYECFdIWEZCVIJ-Jo9AFEpgBCpUBCLYQEAAahwEwgYQCgYEAxNtL4gyjk1P_zAGQyZD2Gu2XkvW_qb_U86yyCGGtv9zdAa35z0YnPy48mGYeIBcyVEKIy3F6XP1HCgSFj3ri_Iv4BD6pBH21GUBTypAKUTf_CL8FkeoxBxuiM8J_1UMZslbWe2SvdcMOwhQwY36dOfyC8UbPkf0pMfVeE3A0PR0gn6yo0AUSmAEKlQEIvBAQABqHATCBhAKBgQCGC990REYYhxd4kXZzDxhg9m9ZDwpEQxL239S2PWpjzfWISGvkSkk-5Tr_Jqxm4tB7f6qmeJL4zkOSvlsH9UXwJ388y-HzFGhzl0fXFpsgwaXGaq3X8SvbwFfPi-YxLl9sVko5b_W7j5JQ8FDLc8TlY41p0Iz03i3-u0uXDEghTSCfz63QBRKYAQqVAQjJEBAAGocBMIGEAoGBALT4SR7BuSUHTQuob630jEdoqbiZwghYlxCza1qf-d5loGU240XHjmm50VVeiqWgorLJaFL9Lc6Z_89tay-0UBhEQFdBfO4AEeWvoiQGyIXZ8YUwXTkY5i_bMPjfTP6OeMnCJkTTYvAUeX6nX2EN9mvnFrFAWpXgtRr-XlpWdCNdIJ_ystAFEpgBCpUBCNEQEAAahwEwgYQCgYEAgfifQeSBpgxwjEXwFAmOd0kivun8g6G91KR66WXK6Muixyj7LpAr2wbT3YKVxXXaXS3oRoV0s69L9pkLKCkSoDvdj_o7PJ5egFqjC-mNzx_VIOQ0bs62a4OyoVLucIzd4aCnHAHJ_RQMRgEAuU-NrD9rcYd1WFNB51yoGOLQYC0gn5W40AUSmAEKlQEI2BAQABqHATCBhAKBgQCKak-ON2HposDiZhSMvtCwCE0QhKt4amvvzCVgHFW4dqjpJt9cNi7qOD7cj2INKY-YwbQa5aO2Mnk6e0b4wASKEjWb7cRyTjPRd0s8paM881YU3H3J32DIAcQXlSuk6_nt0Kp-64ESpiRfuBcsBzILcLlsQdyTp-JgQnv-hLbJvSCfuL3QBRKXAQqUAQjeEBAAGoYBMIGDAoGATooOk9v3SyfM1b8I6yjNlII9I4sZoWVol2yUyv-BPL_AKwxM7hiOb6X5mvWeAhkkFersezp4yNE0eZYNMLqBU0fQ5b1_bfZMA4qgpLkibkEJAUKCypTFjL-zmkZEXu4dDkrFMWXl79FBAzN2NSqLxxYujoKslilvX-oejM1BkU0gn9vC0AUSmAEKlQEI5BAQABqHATCBhAKBgQC613ZOygEcX1COsuwg-IS_vFUuAS1G5vYgLfEQYjClt5nAikIsk7cE9K0Su-CD-zFMtgWb6ndNBLpUyB5gr3hUBkuImS40cqRAvUEDGP0hMQ8A11eyehy8e-Z54vXG2JmotNu3oKf5YjfUlHtr5c9no9uROC8tQWwlKXBzk9LVTSCf_sfQBRKYAQqVAQjsEBAAGocBMIGEAoGBAKUwvGM3EusI4qRFcF7whYXndZ3ylxCgKO_ey8M4TVBjjRwOZmmkUfK9wFfW1vsEnzpQSSBKAJi5LLFsicAitrxS88SiljivtprGh487G-31vjjTs8hYJw3uZzo3Q1YmMf0t8Sp7SJfMET9bELUT8XjL9GdsBEjh0qmahpBulDOVIJ-hzdAFEpgBCpUBCPIQEAAahwEwgYQCgYEAwkEuvLNaZeHbuT_L_FDWT9XEl0gaXIh7ca_dAgP_410kdH9848iv8tOyrKNGswnq5gbwfPOF6OBo3OUMinFvPsUZ1bukXyIvj5qa4rLLVKr-n8CwDBtvDAgb8UdRaJry2V8GlWsXD45Q_30b_2b8FnDtzaub1yN-zD-_xXs0gI0gn8TS0AUSmAEKlQEIhREQABqHATCBhAKBgQCwa_cmx3Fu4XES_qV-nlwloLS7yurajVLMtdigzthanCgK85M8G0Zrt7j1wctaMvgSsuPLuLNolAL1q00vYtLz36uq6YMWEFpkhp47VRljv-SgINbsv0wwcZxCKkUyrAfUpdN8pgec3oAQtHP1K_EftJy6r5_SW1coYeCt3cuKDSCf59fQBQ`
	ticketsTestResponse = `{"252":{"ticket":"3:serv:CNEQEOqy3dAFIgYI-wEQ_AE:FUJBmWDDMCbKTmL5llaLiK3j_L9gxSrwux5EoGv_7fMnsgh14j6I9WbUlpdGNZrEugQLOdBFll8hd84tl6kTVSwu1KFDaMkfEIrzXV4NqHhnoYlm4JvO5olBlgpKdrFA7jb3gFR1qVH3G0OiH4jFaIlVP_cZYFhUfvQdralnjk0"},"253":{"ticket":"3:serv:CNEQEOqy3dAFIgYI-wEQ_QE:Ntk3eoHXVts63D6C8CA2llTLVhO-4xfKacUxCUF40RafJxiu2dytZT2r2sBAxVq1JrwcSR3Qv7On6fAeW2SQkaQcNNtkDrdfh-2j_m6IztNla_teTlLbIvdGw4UZN1KgI005T_aMjQl2JaBnYlIxQjl2ocE9IQb5ZiT1XceYZmg"}}`
)

func TestTvmApi(t *testing.T) {
	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return []byte(keysTestResponse), http.StatusOK, nil
				}
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return []byte(ticketsTestResponse), http.StatusOK, nil
				}

				return nil, http.StatusOK, nil
			},
		},
	}

	tvmClient := NewTvmAPI(&url.URL{Scheme: "http", Host: "localhost:1"}, client)

	_, err := tvmClient.GetKeys()
	if err != nil {
		t.Fatal(err)
	}

	ticks, err := tvmClient.GetTickets(
		"6zQnNi5BpraJplR-EFtfVA",
		251,
		[]tvmtypes.Dst{{ID: 252}, {ID: 253}},
	)
	if err != nil {
		t.Fatal(err)
	}

	str, ok := ticks.Tickets[252]
	if !ok {
		t.Fatal("Ticket for dst 252 not found")
	}
	if len(string(str)) == 0 {
		t.Fatal("Ticket for dst 252 is empty")
	}

	str, ok = ticks.Tickets[253]
	if !ok {
		t.Fatal("Ticket for dst 253 not found")
	}
	if len(string(str)) == 0 {
		t.Fatal("Ticket for dst 253 is empty")
	}

	_, ok = ticks.Tickets[254]
	if ok {
		t.Fatal("Ticket for dst 254 is found")
	}
}

func TestUnreachableTvmApi(t *testing.T) {
	terr := errors.New("kek")
	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return []byte(keysTestResponse), http.StatusOK, terr
				}
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return []byte(ticketsTestResponse), http.StatusOK, terr
				}
				return nil, http.StatusOK, nil
			},
		},
	}
	tvmClient := NewTvmAPI(&url.URL{Scheme: "http", Host: "localhost:1"}, client)

	if _, err := tvmClient.GetKeys(); err == nil {
		t.Fatalf("GetKeys: err")
	}

	_, err := tvmClient.GetTickets("  sdf", 12, []tvmtypes.Dst{})
	require.EqualError(t, err, "sign request failed: invalid base64 in secret")

	_, err = tvmClient.GetTickets("asdf", 12, []tvmtypes.Dst{})
	require.EqualError(t, err, `Post "http://localhost:1/2/ticket": kek`)
}

func TestBadTvmApi(t *testing.T) {
	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return []byte(keysTestResponse), http.StatusBadGateway, nil
				}
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return []byte(ticketsTestResponse), http.StatusBadGateway, nil
				}

				return nil, http.StatusBadGateway, nil
			},
		},
	}

	tvmClient := NewTvmAPI(&url.URL{Scheme: "http", Host: "localhost:1"}, client)

	if _, err := tvmClient.GetKeys(); err == nil {
		t.Fatalf("GetKeys")
	}

	if _, err := tvmClient.GetTickets("asdf", 12, []tvmtypes.Dst{}); err == nil {
		t.Fatalf("GetTickets")
	}
}

func TestBadJsonTickets(t *testing.T) {
	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				return []byte("{asd"), http.StatusOK, nil
			},
		},
	}

	tvmClient := NewTvmAPI(&url.URL{Scheme: "http", Host: "localhost:1"}, client)

	if _, err := tvmClient.GetTickets("asdf", 12, []tvmtypes.Dst{}); err != errorInvalidJSONTickets {
		t.Fatal(err)
	}
}

func TestDstIsNotNumberTickets(t *testing.T) {
	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				return []byte(`{"ololo":{"ticket":"kek"}}`), http.StatusOK, nil
			},
		},
	}

	tvmClient := NewTvmAPI(&url.URL{Scheme: "http", Host: "localhost:1"}, client)

	if _, err := tvmClient.GetTickets("asdf", 12, []tvmtypes.Dst{}); err == nil {
		t.Fatalf("GetTickets: dst is not number")
	}
}

func TestErrorsInTickets(t *testing.T) {
	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				return []byte(`{"123":{"error":"kek1"},"456":{"ticket":"kek2"},"789":{}}`), http.StatusOK, nil
			},
		},
	}

	tvmClient := NewTvmAPI(&url.URL{Scheme: "http", Host: "localhost:1"}, client)

	res, err := tvmClient.GetTickets("asdf", 12, []tvmtypes.Dst{})
	if err != nil {
		t.Fatal(err)
	}

	if le := len(res.Errors); le != 2 {
		t.Fatalf("len(res.Errors): %d", le)
	}
	if str, ok := res.Errors[tvm.ClientID(123)]; !ok {
		t.Fatalf("failed to get error for 123")
	} else if str != "kek1" {
		t.Fatalf("error for 123: %s", str)
	}
	if str, ok := res.Errors[tvm.ClientID(789)]; !ok {
		t.Fatalf("failed to get error for 789")
	} else if str != unknownError {
		t.Fatalf("error for 789: %s", str)
	}

	if le := len(res.Tickets); le != 1 {
		t.Fatalf("len(res.Errors): %d", le)
	}
	if str, ok := res.Tickets[tvm.ClientID(456)]; !ok {
		t.Fatalf("failed to get ticket for 456")
	} else if str != "kek2" {
		t.Fatalf("error for 456: %s", str)
	}
}
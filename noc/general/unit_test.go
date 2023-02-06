package parser

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestXMLParser(t *testing.T) {
	t.Run("Parse operation", func(t *testing.T) {
		p := NewParser()
		xmlData, err := p.XMLParse("testdata/testfile.xml")
		require.NoError(t, err)
		require.Equal(t, 5, len(xmlData.Contents))

		for _, tstContent := range []Content{
			Content{
				IPv4Addrs: []string{"193.105.213.21"},
				Subnet:    "193.105.213.36/30",
				Domain:    "legalrc.biz",
			},
			Content{
				IPv4Addrs: []string{"104.25.197.97"},
				IPv6Addrs: []string{"2606:4700:0020:0000:0000:0000:6819:c661", "2606:4700:0020:0000:0000:0000:6819:c561"},
				Domain:    "www.royalqueenseeds.ru",
				URL:       "http://cannabay.org/"},
		} {
			require.Contains(t, xmlData.Contents, tstContent)
		}
	})

	t.Run("Empty XML", func(t *testing.T) {
		p := NewParser()
		content, err := p.XMLProcess("testdata/empty.xml")
		require.NoError(t, err)
		require.Equal(t, 0, len(content))
	})

	t.Run("Negative cases", func(t *testing.T) {
		p := NewParser()
		_, err := p.XMLParse("testdata/not_exist.xml")
		require.ErrorIs(t, err, os.ErrNotExist)

		_, err = p.XMLParse("testdata/broken.xml")
		require.Error(t, err)
	})
}

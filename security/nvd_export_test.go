package nvd

import "context"

func ParseNVD(indexPageURI string) (Feed, error) {
	return parseNVD(parseNvdOpts{
		ctx:          context.Background(),
		indexPageURI: indexPageURI,
	})
}

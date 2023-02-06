package staff

type Option func(*Client)

func WithUpstream(upstream string) Option {
	return func(c *Client) {
		c.httpc.SetBaseURL(upstream)
	}
}

func WithAuthToken(token string) Option {
	return func(c *Client) {
		c.httpc.SetHeader("Authorization", "OAuth "+token)
	}
}

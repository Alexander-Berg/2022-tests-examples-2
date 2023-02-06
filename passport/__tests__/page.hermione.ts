describe('home page', function () {
  hermione.skip.in(['chrome-grid-320']);
  it('default 1400', async function () {
    await this.browser.yaOpenStory('hermione-homepage', 'default', {
      args: { images: false, graphql: 'FULL_DATA' },
    });
    await this.browser.setWindowSize(1400, 1028);
    await this.browser.assertView('plain', 'body');
  });

  hermione.skip.in(['chrome-grid-320']);
  it('default 1024', async function () {
    await this.browser.yaOpenStory('hermione-homepage', 'default', {
      args: { images: false, graphql: 'FULL_DATA' },
    });
    await this.browser.setWindowSize(1024, 1028);
    await this.browser.assertView('plain', 'body');
  });

  hermione.skip.in(['chrome-grid-320']);
  it('default 820', async function () {
    await this.browser.yaOpenStory('hermione-homepage', 'default', {
      args: { images: false, graphql: 'FULL_DATA' },
    });
    await this.browser.setWindowSize(820, 1028);
    await this.browser.assertView('plain', 'body');
  });

  it('default 320', async function () {
    await this.browser.yaOpenStory('hermione-homepage', 'default', {
      args: { images: false, graphql: 'FULL_DATA' },
    });
    await this.browser.setWindowSize(320, 1028);
    await this.browser.assertView('plain', 'body');
  });

  hermione.skip.in(['chrome-grid-320']);
  it('focus heading 1024', async function () {
    await this.browser.yaOpenStory('hermione-homepage', 'default', {
      args: { images: false, graphql: 'FULL_DATA' },
    });
    await this.browser.setWindowSize(1024, 1028);
    await this.browser.keys(['Tab', '\uE000']);
    await this.browser.assertView('plain', 'body');
  });

  it('focus heading 320', async function () {
    await this.browser.yaOpenStory('hermione-homepage', 'default', {
      args: { images: false, graphql: 'FULL_DATA' },
    });
    await this.browser.setWindowSize(320, 1028);
    await this.browser.keys(['Tab', '\uE000']);
    await this.browser.assertView('plain', 'body');
  });
});

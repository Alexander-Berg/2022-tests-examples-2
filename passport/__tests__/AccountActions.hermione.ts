describe('AccountActions', function () {
  it('loading state', async function () {
    await this.browser.yaOpenStory('hermione-accountactions', 'default', {
      args: { data: 'EMPTY_DATA' },
    });
    await this.browser.assertView('plain', 'body');
  });

  it('partial data', async function () {
    await this.browser.yaOpenStory('hermione-accountactions', 'default', {
      args: { data: 'PARTIAL_DATA' },
    });
    await this.browser.assertView('plain', 'body');
  });

  it('full data', async function () {
    await this.browser.yaOpenStory('hermione-accountactions', 'default', {
      args: { data: 'FULL_DATA' },
    });
    await this.browser.assertView('plain', 'body');
  });
});

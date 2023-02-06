const widget = 'widgets/RecoveryMethods';

describe.skip(widget, function () {
  it('Simple data', async function () {
    await this.browser.yaOpenStory(widget, 'Default', {
      args: { graphql: 'simpleData' },
    });
    await this.browser.assertView('plain', '#root');
  });

  it('Empty data', async function () {
    await this.browser.yaOpenStory(widget, 'Default', {
      args: {
        graphql: 'emptyData',
      },
    });
    await this.browser.assertView('plain', '#root');
  });
});

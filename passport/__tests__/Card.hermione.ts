describe('Card', function () {
  const elements = {
    story: '[data-testid=story]',
  };

  it('Default', async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermionecard', 'hermione-default');
    await browser.assertView('default', elements.story);
  });
});

describe('ListItemView', function () {
  const selectors = {
    root: '[data-testid="root"]',
  };

  describe('alignment', () => {
    it('root top', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:top',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('root center', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:center',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('before top', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:center;alignItemsBefore:top',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('before center', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:top;alignItemsBefore:center',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('content top', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:center;alignItemsContent:top',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('content center', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:top;alignItemsContent:center',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('after top', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:center;alignItemsAfter:top',
      });

      await browser.assertView('plain', selectors.root);
    });

    it('after center', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;height:90px;alignItems:top;alignItemsAfter:center',
      });

      await browser.assertView('plain', selectors.root);
    });
  });

  describe('interactive', () => {
    it('enabled', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;interactive:true',
      });

      await browser.assertView('plain', selectors.root);

      await browser.$(selectors.root).moveTo();

      await browser.assertView('hovered', selectors.root);
    });

    it('disabled', async function () {
      const { browser } = this;

      await browser.yaOpenStory('list-item-view', 'default', {
        args: 'width:300px;interactive:false',
      });

      await browser.assertView('plain', selectors.root);

      await browser.$(selectors.root).moveTo();

      await browser.assertView('hovered', selectors.root);
    });
  });
});

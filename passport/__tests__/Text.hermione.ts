describe('Text', function () {
  const selectors = {
    element: "[data-testid='element']",
  };
  const variants = [
    'display-l',
    'display-m',
    'display-s',
    'heading-xl',
    'heading-l',
    'heading-m',
    'heading-s',
    'text-l',
    'text-l-long',
    'text-m',
    'text-m-long',
    'text-s',
    'text-s-long',
    'text-xs',
    'text-xs-long',
    'text-xxs',
  ];
  const colors = ['inherit', 'primary', 'secondary', 'tertiary', 'positive', 'negative'];

  describe('colors', () => {
    ['light', 'dark'].forEach((colorSchema) => {
      describe(colorSchema, () => {
        colors.forEach((color) => {
          it(color, async function () {
            const { browser } = this;

            await browser.yaOpenStory('text', 'default', {
              globals: `colorSchema:${colorSchema}`,
              args: `color:${color};as:div`,
            });

            await browser.assertView('plain', selectors.element);
          });
        });
      });
    });
  });

  describe('variants', () => {
    variants.forEach((variant) => {
      it(variant, async function () {
        const { browser } = this;

        await browser.yaOpenStory('text', 'default', {
          args: `variant:${variant};as:div`,
        });

        await browser.assertView('plain', selectors.element);
      });
    });
  });

  describe('weights', () => {
    ['regular', 'medium', 'bold'].forEach((weight) => {
      it(weight, async function () {
        const { browser } = this;

        await browser.yaOpenStory('text', 'default', {
          args: `weight:${weight};as:div`,
        });

        await browser.assertView('plain', selectors.element);
      });
    });
  });
});

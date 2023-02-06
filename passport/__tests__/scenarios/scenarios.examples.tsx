import { Meta } from '@storybook/react';
import { IS_TESTING } from '@yandex-lego/components/lib/env';

export * from './default';

export default {
  id: 'HermioneCard',
  title: 'Hermione/Card',
  excludeStories: !IS_TESTING ? /Hermione/ : null,
} as Meta;

export * from './common';
export * from './interactive';

export default {
  title: 'Hermione/Shortcut',
  excludeStories: process.env.NODE_ENV === 'production' ? /Hermione/ : null,
};

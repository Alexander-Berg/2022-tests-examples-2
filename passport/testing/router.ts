import Router from 'next-router-mock';

// @ts-expect-error
Router.ready = () => null;

export default Router;

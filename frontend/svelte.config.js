import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // Single-page app: every route is served from index.html and rendered
    // on the client. The Python backend serves this directory in production.
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      strict: true
    })
  }
};

export default config;

// SPA mode: no server-side rendering and no prerendering. The app is built to
// static files by adapter-static and served by the FastAPI backend, which has
// no Node runtime. All data comes from /api.
export const ssr = false;
export const prerender = false;

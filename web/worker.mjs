import assets from 'coursekin:assets';
import { visitorAnswer } from './visitor-answer.mjs';

export default {
  async fetch(request) {
    const path = new URL(request.url).pathname;
    if (path === '/api/answer/visitor') return visitorAnswer(request);
    if (!['GET', 'HEAD'].includes(request.method)) return new Response('Method not allowed.', { status: 405 });
    const asset = assets[path === '/index.html' ? '/' : path];
    if (!asset) return new Response('Not found.', { status: 404 });
    return new Response(request.method === 'HEAD' ? null : Uint8Array.from(atob(asset.data), c => c.charCodeAt(0)), {
      headers: { 'Content-Type': asset.type, 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' },
    });
  },
};

import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://medix-5bc.pages.dev',
  integrations: [
    starlight({
      title: 'Medix',
      description:
        'A fancy command-line media format converter powered by FFmpeg.',
      tagline: 'Batch media conversion with a polished terminal UI.',
      social: {
        github: 'https://github.com/vineethkrishnan/medix',
      },
      editLink: {
        baseUrl: 'https://github.com/vineethkrishnan/medix/edit/main/docs/',
      },
      lastUpdated: true,
      pagination: true,
      customCss: ['./src/styles/custom.css'],
      head: [
        {
          tag: 'meta',
          attrs: { name: 'theme-color', content: '#8b5cf6' },
        },
      ],
      sidebar: [
        {
          label: 'Introduction',
          items: [{ label: 'Features', slug: 'features' }],
        },
        {
          label: 'Getting Started',
          autogenerate: { directory: 'getting-started' },
        },
        {
          label: 'Guides',
          autogenerate: { directory: 'guides' },
        },
        {
          label: 'Reference',
          autogenerate: { directory: 'reference' },
        },
        {
          label: 'Development',
          autogenerate: { directory: 'development' },
        },
        {
          label: 'Roadmap',
          slug: 'roadmap',
          badge: { text: 'Upcoming', variant: 'tip' },
        },
      ],
    }),
  ],
});

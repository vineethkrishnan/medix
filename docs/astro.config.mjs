import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://medix.pages.dev',
  integrations: [
    starlight({
      title: 'Medix',
      description:
        'A fancy command-line media format converter powered by FFmpeg.',
      tagline: 'Batch media conversion with a polished terminal UI.',
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/vineethkrishnan/medix',
        },
        {
          icon: 'seti:python',
          label: 'PyPI',
          href: 'https://pypi.org/project/medix/',
        },
      ],
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
          items: [
            { label: 'What is Medix?', link: '/' },
            { label: 'Features', link: '/features/' },
          ],
        },
        {
          label: 'Getting Started',
          items: [
            { label: 'Requirements', link: '/getting-started/requirements/' },
            { label: 'Installation', link: '/getting-started/installation/' },
            { label: 'Quick Start', link: '/getting-started/quick-start/' },
          ],
        },
        {
          label: 'Guides',
          items: [
            { label: 'CLI Usage', link: '/guides/cli-usage/' },
            { label: 'Dry Run Mode', link: '/guides/dry-run/' },
            { label: 'Formats & Codecs', link: '/guides/formats/' },
            { label: 'Advanced Settings', link: '/guides/advanced-settings/' },
            { label: 'FFmpeg Auto-Install', link: '/guides/ffmpeg-setup/' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'CLI Reference', link: '/reference/cli/' },
            { label: 'Supported Formats', link: '/reference/supported-formats/' },
          ],
        },
        {
          label: 'Development',
          items: [
            { label: 'Contributing', link: '/development/contributing/' },
            { label: 'Testing', link: '/development/testing/' },
            { label: 'Release Process', link: '/development/releases/' },
          ],
        },
        {
          label: 'Roadmap',
          link: '/roadmap/',
          badge: { text: 'Upcoming', variant: 'tip' },
        },
      ],
    }),
  ],
});

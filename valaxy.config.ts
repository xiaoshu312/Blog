import type { UserThemeConfig } from 'valaxy-theme-yun'
import { defineValaxyConfig } from 'valaxy'

// add icons what you will need
const safelist = [
  'i-ri-home-line',
]

/**
 * User Config
 */
export default defineValaxyConfig<UserThemeConfig>({
  // site config see site.config.ts

  theme: 'yun',

  themeConfig: {
    banner: {
      enable: false,
      title: '小树的小窝',
    },

    pages: [
      {
        name: '我的小伙伴们',
        url: '/links/',
        icon: 'i-fluent-person-32-regular',
        color: 'dodgerblue',
      },
    ],

    footer: {
      since: 2026,
      beian: {
        enable: true,
        icp: '京ICP备2025149863号-1',
        police: '',
      },
    },
  },

  unocss: { safelist },
})

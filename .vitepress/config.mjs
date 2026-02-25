import { defineConfig } from 'vitepress'
import headConfig from './config/head'
import enThemeConfig from './config/en'
import zhThemeConfig from './config/zh'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  srcDir: "docs",
  
  title: "Xiaoshu312's Blog",
  description: "Xiaoshu312's Blog",
  cleanUrls: true,
  locales: {
    root: {
      label: 'English',
      lang: 'en',
    },
    zh: {
      label: '简体中文',
      lang: 'zh',
      link: '/zh/',
      themeConfig: zhThemeConfig,
    },
  },
  themeConfig: enThemeConfig,
  headConfig: headConfig,
  sitemap: {
    hostname: 'https://blog.xiaoshu312.top/',
  },
  lastUpdated: true,
})

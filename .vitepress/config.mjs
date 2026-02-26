import { defineConfig } from 'vitepress'
import headConfig from './config/head'
import enThemeConfig from './config/en'
import zhThemeConfig from './config/zh'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  srcDir: "docs",
  
  title: "Xiaoshu312's Home",
  description: "A Normal Blog",
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
      title: "小树的小窝",
      description: "一个普通的博客。",
    },
  },
  themeConfig: enThemeConfig,
  head: headConfig,
  sitemap: {
    hostname: 'https://blog.xiaoshu312.top/',
  },
  lastUpdated: true,

  markdown: {
    lineNumbers: true,
    config(md) {
      const fence = md.renderer.rules.fence
      md.renderer.rules.fence = function (tokens, idx, options, env, self) {
        const { localeIndex = 'root' } = env
        const codeCopyButtonTitle = (() => {
          switch (localeIndex) {
            case 'es':
              return 'Copiar código'
            case 'fa':
              return 'کپی کد'
            case 'ko':
              return '코드 복사'
            case 'pt':
              return 'Copiar código'
            case 'ru':
              return 'Скопировать код'
            case 'zh':
              return '复制代码'
            default:
              return 'Copy code'
          }
        })()
        return fence(tokens, idx, options, env, self).replace(
          '<button title="Copy Code" class="copy"></button>',
          `<button title="${codeCopyButtonTitle}" class="copy"></button>`
        )
      }
    },
  },
})

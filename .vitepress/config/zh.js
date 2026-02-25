const zhThemeConfig = {
    // https://vitepress.dev/reference/default-theme-config
    logo: '/logo.png',

    i18nRouting: true,

    nav: [
        { text: '主页', link: '/zh/' },
    ],

    sidebar: [
        {
            text: '',
            items: [
                // { text: 'Text', link: '/zh/path-to-page' },
            ]
        }
    ],

    socialLinks: [
        { icon: 'github', link: 'https://github.com/zhiyiYo/Fluent-M3U8' },
        { icon: 'kofi', link: 'https://ko-fi.com/zhiyiYo' },
        { icon: 'afdian', link: 'https://afdian.com/a/zhiyiyo' },
    ],

    footer: {
        message: `基于 <a href="https://github.com/xiaoshu312/Blog/blob/main/LICENSE">CC BY-NC-SA 4.0 许可</a>发布.`,
        copyright: '版权所有 © 2026 xiaoshu312.'
    },

    editLink: {
        pattern: 'https://github.com/xiaoshu312/Blog/edit/main/docs/:path',
        text: "在 GitHub 上编辑此页面"
    },

    lastUpdatedText: '最后更新于',
    returnToTopLabel: '返回顶部',

    docFooter: {
        prev: '上一页',
        next: '下一页'
    },

    outline: {
        level: "deep", // 右侧大纲标题层级
        label: "目录", // 右侧大纲标题文本配置
    }
}

export default zhThemeConfig
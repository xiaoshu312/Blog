const enThemeConfig = {
    // https://vitepress.dev/reference/default-theme-config
    logo: '/logo.png',

    i18nRouting: true,

    nav: [
        { text: 'Home', link: '/' },
    ],

    sidebar: [
        {
            text: '',
            items: [
                // { text: 'Text', link: '/link-to-page' },
            ]
        }
    ],

    socialLinks: [
        { icon: 'github', link: 'https://github.com/xiaoshu312/Blog' },
        { icon: 'afdian', link: 'https://afdian.com/a/xiaoshu312' },
    ],

    footer: {
        message: `Released under the <a href="https://github.com/xiaoshu312/Blog/blob/main/LICENSE">CC BY-NC-SA 4.0 License</a>.`,
        copyright: '© 2026 xiaoshu312. All rights reserved.'
    },

    editLink: {
        pattern: 'https://github.com/xiaoshu312/Blog/edit/main/docs/:path',
        text: "Edit this page on GitHub"
    },

    outline: {
        level: "deep", // 右侧大纲标题层级
    }
}

export default enThemeConfig
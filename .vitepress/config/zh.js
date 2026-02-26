const zhThemeConfig = {
    // https://vitepress.dev/reference/default-theme-config
    logo: '/my_icon.jpg',

    i18nRouting: true,

    siteTitle: '小树的小窝',

    search: {
      provider: 'local',
      options: {
        locales: {
          zh: { // 如果你想翻译默认语言，请将此处设为 `root`
            translations: {
              button: {
                buttonText: '搜索',
                buttonAriaLabel: '搜索',
              },
              modal: {
                displayDetails: '显示详细列表',
                resetButtonTitle: '重置搜索',
                backButtonTitle: '关闭搜索',
                noResultsText: '没有结果',
                footer: {
                  selectText: '选择',
                  selectKeyAriaLabel: '输入',
                  navigateText: '导航',
                  navigateUpKeyAriaLabel: '上箭头',
                  navigateDownKeyAriaLabel: '下箭头',
                  closeText: '关闭',
                  closeKeyAriaLabel: 'Esc',
                },
              },
            },
          },
        },
      },
    },

    nav: [
        { text: '主页', link: '/zh/' },
    ],

    // sidebar: [
    //     {
    //         text: '',
    //         items: [
    //             { text: 'Text', link: '/zh/path-to-page' },
    //         ]
    //     }
    // ],

    socialLinks: [
        { icon: 'github', link: 'https://github.com/xiaoshu312/Blog' },
        { icon: 'afdian', link: 'https://afdian.com/a/xiaoshu312' },
    ],

    footer: {
        message: `基于 <a href="https://github.com/xiaoshu312/Blog/blob/main/LICENSE">CC BY-NC-SA 4.0 许可证</a>发布.`,
        copyright: '版权所有 © 2026 xiaoshu312.'
    },

    editLink: {
        pattern: 'https://github.com/xiaoshu312/Blog/edit/main/docs/:path',
        text: "在 GitHub 上编辑此页面"
    },

    docFooter: {
        prev: '上一页',
        next: '下一页'
    },

    outline: {
        level: "deep", // 右侧大纲标题层级
        label: "目录", // 右侧大纲标题文本配置
    },

    lastUpdatedText: '最后更新于',
    returnToTopLabel: '返回顶部',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    sidebarMenuLabel: '菜单',
    langMenuLabel: '切换语言',
}

export default zhThemeConfig
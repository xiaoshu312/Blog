import { defineSiteConfig } from 'valaxy'

export default defineSiteConfig({
  url: 'https://blog.xiaoshu312.top/',
  lang: 'zh-CN',
  title: '小树的小窝',
  author: {
    name: '小树的小窝',
  },
  description: 'GitHub: XiaoshuDeXiaowo / xiaoshu312',
  social: [
    // {
    //   name: 'RSS',
    //   link: '/atom.xml',
    //   icon: 'i-ri-rss-line',
    //   color: 'orange',
    // },
    {
      name: 'GitHub',
      link: 'https://github.com/XiaoshuDeXiaowo',
      icon: 'i-ri-github-line',
      color: '#6e5494',
    },
    {
      name: '网易云音乐',
      link: 'https://music.163.com/#/user?id=6420046839',
      icon: 'i-ri-netease-cloud-music-line',
      color: '#C20C0C',
    },
    {
      name: '哔哩哔哩',
      link: 'https://space.bilibili.com/3537108350273794',
      icon: 'i-ri-bilibili-line',
      color: '#FF8EB3',
    },
    {
      name: 'E-Mail',
      link: 'mailto:xiaoshu312@outlook.com',
      icon: 'i-ri-mail-line',
      color: '#8E71C1',
    },
  ],

  search: {
    enable: true,
  },

  sponsor: {
    enable: true,
    title: '支持一下！',
    methods: [
      {
        name: '支付宝',
        url: 'https://files.xiaoshu312.top/qrcode/alipay.jpg',
        color: '#00A3EE',
        icon: 'i-ri-alipay-line',
      },
      {
        name: '微信支付',
        url: 'https://files.xiaoshu312.top/qrcode/wechatpay.jpg',
        color: '#2DC100',
        icon: 'i-ri-wechat-pay-line',
      },
    ],
  },
})

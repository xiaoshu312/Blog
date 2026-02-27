import DefaultTheme from 'vitepress/theme'
import CardWidget from './components/CardWidget.vue'
import './custom.css'
import Layout from './Layout.vue'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component('CardWidget', CardWidget)
  }
}
import DefaultTheme from 'vitepress/theme'
import CardWidget from './components/CardWidget.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('CardWidget', CardWidget)
  }
}
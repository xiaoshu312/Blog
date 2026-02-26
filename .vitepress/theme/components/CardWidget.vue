<template>
  <component
    :is="href ? 'a' : 'div'"
    :href="href"
    :target="isExternal ? '_blank' : undefined"
    :rel="isExternal ? 'noreferrer' : undefined"
    class="card-widget"
    :class="{ 'card-link': href }"
  >
    <div class="card-header">
      <h2 class="card-title">{{ title }}</h2>
      <h3 v-if="subtitle" class="card-subtitle">{{ subtitle }}</h3>
    </div>
    <div class="card-content">
      <slot />
    </div>
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  href: { type: String, default: null }
})

const isExternal = computed(() => {
  if (!props.href) return false
  return /^(https?:)?\/\//.test(props.href) ||
         props.href.startsWith('mailto:') ||
         props.href.startsWith('tel:')
})
</script>

<style scoped>
.card-widget {
  display: block;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
  background-color: var(--vp-c-bg-soft);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s, border-color 0.3s;
  text-decoration: none;
  color: inherit;
}

.card-widget:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--vp-c-brand);
}

.card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 12px;
  border-bottom: 1px dashed var(--vp-c-divider);
  padding-bottom: 8px;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: var(--vp-c-text-1);
  text-align: center;
}

.card-subtitle {
  font-size: 1.2rem;
  font-weight: 500;
  color: var(--vp-c-text-2);
  margin: 4px 0 0 0;
  text-align: center;
}

.card-content {
  font-size: 0.95rem;
  color: var(--vp-c-text-1);
  line-height: 1.6;
}

/* 完整 Markdown 元素样式 */
.card-content :deep(p) {
  margin: 8px 0;
}
.card-content :deep(p:first-child) {
  margin-top: 0;
}
.card-content :deep(p:last-child) {
  margin-bottom: 0;
}

.card-content :deep(ul),
.card-content :deep(ol) {
  padding-left: 1.5rem;
  margin: 8px 0;
}

.card-content :deep(li) {
  margin: 4px 0;
}

.card-content :deep(blockquote) {
  border-left: 4px solid var(--vp-c-divider);
  padding-left: 1rem;
  color: var(--vp-c-text-2);
  margin: 8px 0;
}

.card-content :deep(code) {
  background-color: var(--vp-c-bg-mute);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.card-content :deep(pre) {
  background-color: var(--vp-c-bg-soft);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.card-content :deep(a) {
  color: var(--vp-c-brand);
  text-decoration: none;
}
.card-content :deep(a:hover) {
  text-decoration: underline;
}

.card-content :deep(h1),
.card-content :deep(h2),
.card-content :deep(h3),
.card-content :deep(h4) {
  margin: 16px 0 8px;
  font-weight: 600;
}
</style>
<template>
  <div class="card-widget">
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <p v-if="formattedDate" class="card-date">{{ formattedDate }}</p>
    </div>
    <div class="card-content">
      <!-- 默认插槽，支持 Markdown 内容 -->
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  date: {
    type: [String, Date, Number],
    default: null
  }
})

const formattedDate = computed(() => {
  if (!props.date) return null
  const dateObj = new Date(props.date)
  if (isNaN(dateObj)) return null
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${year}/${month}/${day}`
})
</script>

<style scoped>
.card-widget {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
  background-color: var(--vp-c-bg-soft);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s, border-color 0.3s;
}

.card-widget:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--vp-c-brand);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  border-bottom: 1px dashed var(--vp-c-divider);
  padding-bottom: 8px;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: var(--vp-c-text-1);
}

.card-date {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  margin: 0;
  background: var(--vp-c-bg-mute);
  padding: 2px 8px;
  border-radius: 16px;
  white-space: nowrap;
}

.card-content {
  font-size: 0.95rem;
  color: var(--vp-c-text-1);
  line-height: 1.6;
}

/* 保证插槽内 Markdown 元素的边距干净 */
.card-content :deep(p) {
  margin: 8px 0;
}
.card-content :deep(p:first-child) {
  margin-top: 0;
}
.card-content :deep(p:last-child) {
  margin-bottom: 0;
}
</style>
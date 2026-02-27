<!-- Layout.vue -->
<template>
  <Layout>
    <template #doc-after>
      <div style="margin-top: 24px">
        <Giscus
          :key="page.filePath"
          repo="xiaoshu312/Blog"
          repo-id="R_kgDORYiXEw"
          category="Announcements"
          category-id="DIC_kwDORYiXE84C3UFo"
          mapping="pathname"
          strict="1"
          reactions-enabled="1"
          emit-metadata="0"
          input-position="top"
          theme="preferred_color_scheme"
          lang="zh-CN"
          crossorigin="anonymous"
        />
      </div>
    </template>
  </Layout>
</template>

<script lang="ts" setup>
import Giscus from "@giscus/vue";
import DefaultTheme from "vitepress/theme";
import { useData } from "vitepress";

const { page } = useData();

const { Layout } = DefaultTheme;
</script>
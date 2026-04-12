<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const isEdit = computed(() => Boolean(route.params.id))
</script>

<template>
  <section class="rounded-lg border border-stone-200 bg-white p-6">
    <h1 class="text-2xl font-semibold text-stone-800">
      {{ isEdit ? '编辑博客（占位）' : '新建博客（占位）' }}
    </h1>
    <p class="mt-2 text-sm text-stone-500">
      这是阶段2页面骨架，后续阶段再接入真实表单与提交逻辑。
    </p>
    <p v-if="isEdit" class="mt-2 text-sm text-stone-600">当前编辑 ID：{{ route.params.id }}</p>

    <div class="mt-6 flex flex-wrap gap-4 text-sm">
      <RouterLink to="/blog" class="font-medium text-stone-700 underline-offset-2 hover:underline">
        返回博客列表
      </RouterLink>
    </div>
  </section>
</template>

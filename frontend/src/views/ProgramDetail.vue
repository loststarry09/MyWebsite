<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { findProgramById } from '../data/programs'

const route = useRoute()
const program = computed(() => findProgramById(route.params.id))
</script>

<template>
  <section class="rounded-lg border border-stone-200 bg-white p-6 transition-colors duration-300 dark:border-stone-700 dark:bg-stone-800">
    <template v-if="program">
      <h1 class="text-2xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">{{ program.name }}</h1>
      <p class="mt-2 text-sm text-stone-600 transition-colors duration-300 dark:text-stone-300">{{ program.summary }}</p>

      <div class="mt-4">
        <h2 class="text-sm font-medium text-stone-700 transition-colors duration-300 dark:text-stone-200">技术栈</h2>
        <ul class="mt-2 flex flex-wrap gap-2">
          <li
            v-for="item in program.stack"
            :key="item"
            class="rounded border border-stone-200 px-2 py-1 text-xs text-stone-500 transition-colors duration-300 dark:border-stone-600 dark:text-stone-400"
          >
            {{ item }}
          </li>
        </ul>
      </div>

      <p class="mt-4 text-sm text-stone-600 transition-colors duration-300 dark:text-stone-300">
        当前状态：
        <span class="font-medium text-stone-700 transition-colors duration-300 dark:text-stone-200">{{ program.status }}</span>
      </p>
    </template>

    <template v-else>
      <h1 class="text-2xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">未找到程序</h1>
      <p class="mt-2 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">没有匹配 ID 为“{{ route.params.id }}”的项目。</p>
    </template>

    <RouterLink
      to="/programs"
      class="mt-6 inline-flex text-sm font-medium text-stone-700 underline-offset-2 transition-colors duration-300 hover:underline dark:text-stone-300"
    >
      返回程序列表
    </RouterLink>
  </section>
</template>

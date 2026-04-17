<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="space-y-4 rounded-lg border border-stone-200 bg-white p-6 transition-colors duration-300 dark:border-stone-700 dark:bg-stone-800">
    <header>
      <h1 class="text-2xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">个人主页</h1>
      <p class="mt-2 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">
        欢迎来到我的小站，这里记录我的项目、学习笔记与一些轻松内容。
      </p>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="rounded-lg border border-stone-200 p-4 transition-colors duration-300 dark:border-stone-700">
        <h2 class="text-sm font-medium text-stone-700 transition-colors duration-300 dark:text-stone-200">目前在做</h2>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-stone-600 transition-colors duration-300 dark:text-stone-300">
          <li>持续完善个人网站前端体验</li>
          <li>整理并补充项目展示内容</li>
          <li>优化部署与维护流程</li>
        </ul>
      </article>

      <article class="rounded-lg border border-stone-200 p-4 transition-colors duration-300 dark:border-stone-700">
        <h2 class="text-sm font-medium text-stone-700 transition-colors duration-300 dark:text-stone-200">快速入口</h2>
        <div class="mt-3 flex flex-wrap gap-2">
          <RouterLink
            to="/programs"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 transition-colors duration-300 hover:bg-stone-50 dark:border-stone-600 dark:text-stone-200 dark:hover:bg-stone-700"
          >
            看我的程序
          </RouterLink>
          <RouterLink
            to="/fun"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 transition-colors duration-300 hover:bg-stone-50 dark:border-stone-600 dark:text-stone-200 dark:hover:bg-stone-700"
          >
            去娱乐页面
          </RouterLink>
          <RouterLink
            to="/blog"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 transition-colors duration-300 hover:bg-stone-50 dark:border-stone-600 dark:text-stone-200 dark:hover:bg-stone-700"
          >
            站内博客
          </RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

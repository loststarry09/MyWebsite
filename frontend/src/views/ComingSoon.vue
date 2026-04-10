<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="space-y-4 rounded-lg border border-stone-200 bg-white p-6">
    <header>
      <h1 class="text-2xl font-semibold text-stone-800">个人主页</h1>
      <p class="mt-2 text-sm text-stone-500">
        欢迎来到我的小站，这里记录我的项目、学习笔记与一些轻松内容。
      </p>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="rounded-lg border border-stone-200 p-4">
        <h2 class="text-sm font-medium text-stone-700">目前在做</h2>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-stone-600">
          <li>持续完善个人网站前端体验</li>
          <li>整理并补充项目展示内容</li>
          <li>优化部署与维护流程</li>
        </ul>
      </article>

      <article class="rounded-lg border border-stone-200 p-4">
        <h2 class="text-sm font-medium text-stone-700">快速入口</h2>
        <div class="mt-3 flex flex-wrap gap-2">
          <RouterLink
            to="/programs"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 hover:bg-stone-50"
          >
            看我的程序
          </RouterLink>
          <RouterLink
            to="/fun"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 hover:bg-stone-50"
          >
            去娱乐页面
          </RouterLink>
          <a
            href="https://example.com"
            target="_blank"
            rel="noopener noreferrer"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 hover:bg-stone-50"
          >
            外部博客
          </a>
        </div>
      </article>
    </div>
  </section>
</template>

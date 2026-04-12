<script setup>
import NavCard from '../components/NavCard.vue'
</script>

<template>
  <section class="flex min-h-[70vh] items-center justify-center transition-colors duration-300">
    <div class="w-full max-w-3xl">
      <h1 class="mb-8 text-center text-3xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">个人导航</h1>
      <div class="grid gap-4 sm:grid-cols-2">
        <NavCard title="个人主页" subtitle="查看简介" to="/coming-soon" />
        <NavCard
          title="博客"
          subtitle="查看站内博客"
          to="/blog"
        />
        <NavCard title="我的程序" subtitle="查看项目列表" to="/programs" />
        <NavCard title="娱乐" subtitle="轻松一下" to="/fun" />
      </div>
    </div>
  </section>
</template>

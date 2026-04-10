<script setup>
import { RouterLink } from 'vue-router'
import { programs } from '../data/programs'
</script>

<template>
  <section class="rounded-lg border border-stone-200 bg-white p-6">
    <h1 class="text-2xl font-semibold text-stone-800">我的程序</h1>
    <p class="mt-2 text-sm text-stone-500">这里收录我正在做或计划中的小项目。</p>

    <div class="mt-6 grid gap-4 sm:grid-cols-2">
      <article
        v-for="program in programs"
        :key="program.id"
        class="rounded-lg border border-stone-200 p-4 transition hover:border-stone-400"
      >
        <div class="flex items-center justify-between gap-2">
          <h2 class="text-base font-medium text-stone-800">{{ program.name }}</h2>
          <span class="rounded bg-stone-100 px-2 py-1 text-xs text-stone-600">
            {{ program.status }}
          </span>
        </div>
        <p class="mt-2 text-sm text-stone-600">{{ program.summary }}</p>
        <ul class="mt-3 flex flex-wrap gap-2">
          <li
            v-for="item in program.stack"
            :key="`${program.id}-${item}`"
            class="rounded border border-stone-200 px-2 py-1 text-xs text-stone-500"
          >
            {{ item }}
          </li>
        </ul>
        <RouterLink
          :to="`/program/${program.id}`"
          class="mt-4 inline-flex text-sm font-medium text-stone-700 underline-offset-2 hover:underline"
        >
          查看详情
        </RouterLink>
      </article>
    </div>
  </section>
</template>

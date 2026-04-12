<script setup>
defineProps({
  blog: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition-colors duration-300 dark:border-stone-700 dark:bg-stone-900">
    <div class="flex items-center justify-between gap-3">
      <h2 class="text-base font-medium text-stone-800 transition-colors duration-300 dark:text-stone-100">{{ blog.title }}</h2>
      <span
        v-if="blog.isFavorite"
        class="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700 transition-colors duration-300 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
      >
        收藏
      </span>
    </div>

    <ul v-if="Array.isArray(blog.tags) && blog.tags.length" class="mt-3 flex flex-wrap gap-2">
      <li
        v-for="tag in blog.tags"
        :key="`${blog.id}-${tag}`"
        class="rounded border border-stone-200 px-2 py-1 text-xs text-stone-500 transition-colors duration-300 dark:border-stone-600 dark:text-stone-400"
      >
        #{{ tag }}
      </li>
    </ul>

    <RouterLink
      :to="`/blog/${blog.id}`"
      class="mt-4 inline-flex text-sm font-medium text-stone-700 underline-offset-2 transition-colors duration-300 hover:underline dark:text-stone-300"
    >
      查看详情
    </RouterLink>
  </article>
</template>

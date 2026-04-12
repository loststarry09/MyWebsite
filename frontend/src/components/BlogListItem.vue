<script setup>
defineProps({
  blog: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
    <div class="flex items-center justify-between gap-3">
      <h2 class="text-base font-medium text-stone-800">{{ blog.title }}</h2>
      <span
        v-if="blog.isFavorite"
        class="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700"
      >
        收藏
      </span>
    </div>

    <ul v-if="Array.isArray(blog.tags) && blog.tags.length" class="mt-3 flex flex-wrap gap-2">
      <li
        v-for="tag in blog.tags"
        :key="`${blog.id}-${tag}`"
        class="rounded border border-stone-200 px-2 py-1 text-xs text-stone-500"
      >
        #{{ tag }}
      </li>
    </ul>

    <RouterLink
      :to="`/blog/${blog.id}`"
      class="mt-4 inline-flex text-sm font-medium text-stone-700 underline-offset-2 hover:underline"
    >
      查看详情
    </RouterLink>
  </article>
</template>

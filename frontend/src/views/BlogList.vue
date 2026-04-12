<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

const blogs = ref([])
const loading = ref(true)
const loadError = ref('')

async function fetchBlogs() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await axios.get('/api/blogs')
    blogs.value = Array.isArray(data) ? data : []
  } catch {
    loadError.value = '博客加载失败，请稍后重试。'
    blogs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchBlogs)
</script>

<template>
  <section class="rounded-xl border border-stone-200 bg-[#F7F5F2] p-6 shadow-sm transition hover:shadow-md">
    <div class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-stone-800">博客</h1>
        <p class="mt-2 text-sm text-stone-500">这里是站内博客列表。</p>
      </div>
      <RouterLink
        to="/blog/new"
        class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
      >
        新建博客（占位）
      </RouterLink>
    </div>

    <p v-if="loading" class="mt-6 text-sm text-stone-500">加载中...</p>
    <p v-else-if="loadError" class="mt-6 text-sm text-rose-600">{{ loadError }}</p>
    <p v-else-if="!blogs.length" class="mt-6 text-sm text-stone-500">暂时还没有博客内容。</p>

    <div v-else class="mt-6 grid gap-4">
      <article
        v-for="blog in blogs"
        :key="blog.id"
        class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
      >
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-base font-medium text-stone-800">{{ blog.title }}</h2>
          <span
            v-if="blog.isFavorite"
            class="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700"
          >
            收藏
          </span>
        </div>
        <p class="mt-2 line-clamp-3 text-sm text-stone-600">{{ blog.content }}</p>

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
        <RouterLink
          :to="`/blog/edit/${blog.id}`"
          class="ml-4 mt-4 inline-flex text-sm font-medium text-stone-700 underline-offset-2 hover:underline"
        >
          编辑页面（占位）
        </RouterLink>
      </article>
    </div>
  </section>
</template>

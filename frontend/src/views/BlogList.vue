<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import BlogListItem from '../components/BlogListItem.vue'

const blogs = ref([])
const loading = ref(true)
const loadError = ref('')

async function fetchBlogs() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await axios.get('/api/blogs')
    blogs.value = Array.isArray(data) ? data : []
  } catch (error) {
    loadError.value = '博客列表加载失败，请稍后重试。'
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
        新建博客
      </RouterLink>
    </div>

    <p v-if="loading" class="mt-6 text-sm text-stone-500">加载中...</p>
    <p v-else-if="loadError" class="mt-6 text-sm text-rose-600">{{ loadError }}</p>
    <p v-else-if="!blogs.length" class="mt-6 text-sm text-stone-500">暂时还没有博客内容。</p>
    <div v-else class="mt-6 grid gap-4">
      <BlogListItem
        v-for="blog in blogs"
        :key="blog.id"
        :blog="blog"
      />
    </div>
  </section>
</template>

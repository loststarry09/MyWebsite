<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import BlogListItem from '../components/BlogListItem.vue'

const blogs = ref([])
const loading = ref(true)
const loadError = ref('')
const selectedTag = ref('')
const favoritesOnly = ref(false)

const allTags = computed(() => {
  const tagSet = new Set()
  blogs.value.forEach((blog) => {
    if (Array.isArray(blog.tags)) {
      blog.tags.forEach((tag) => {
        if (tag) tagSet.add(tag)
      })
    }
  })
  return [...tagSet]
})

const filteredBlogs = computed(() =>
  blogs.value.filter((blog) => {
    const matchFavorite = !favoritesOnly.value || Boolean(blog.isFavorite)
    const matchTag =
      !selectedTag.value || (Array.isArray(blog.tags) && blog.tags.includes(selectedTag.value))
    return matchFavorite && matchTag
  })
)

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
  <section class="rounded-xl border border-stone-200 bg-[#F7F5F2] p-6 shadow-sm transition-colors duration-300 hover:shadow-md dark:border-stone-700 dark:bg-stone-800">
    <div class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">博客</h1>
        <p class="mt-2 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">这里是站内博客列表。</p>
      </div>
      <RouterLink
        to="/blog/new"
        class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:shadow dark:border-stone-600 dark:bg-stone-700 dark:text-stone-200 dark:hover:bg-stone-600"
      >
        新建博客
      </RouterLink>
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-4 text-sm text-stone-600 transition-colors duration-300 dark:text-stone-300">
      <label class="flex items-center gap-2">
        标签筛选
        <select
          v-model="selectedTag"
          class="rounded border border-stone-300 bg-white px-2 py-1 text-sm text-stone-700 transition-colors duration-300 dark:border-stone-600 dark:bg-stone-900 dark:text-stone-200"
        >
          <option value="">全部</option>
          <option v-for="tag in allTags" :key="tag" :value="tag">{{ tag }}</option>
        </select>
      </label>

      <label class="inline-flex items-center gap-2">
        <input v-model="favoritesOnly" type="checkbox" />
        只看收藏
      </label>
    </div>

    <p v-if="loading" class="mt-6 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">加载中...</p>
    <p v-else-if="loadError" class="mt-6 text-sm text-rose-600">{{ loadError }}</p>
    <p v-else-if="!filteredBlogs.length" class="mt-6 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">没有符合条件的博客。</p>
    <div v-else class="mt-6 grid gap-4">
      <BlogListItem
        v-for="blog in filteredBlogs"
        :key="blog.id"
        :blog="blog"
      />
    </div>
  </section>
</template>

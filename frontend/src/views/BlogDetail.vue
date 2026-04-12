<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const blog = ref(null)
const loading = ref(true)
const loadError = ref('')
const deleting = ref(false)

async function fetchBlog() {
  loading.value = true
  loadError.value = ''
  blog.value = null
  try {
    const { data } = await axios.get(`/api/blog/${route.params.id}`)
    blog.value = data
  } catch (error) {
    if (error?.response?.status === 404) {
      loadError.value = '未找到该博客。'
    } else {
      loadError.value = '博客加载失败，请稍后重试。'
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchBlog)

async function deleteBlog() {
  if (!blog.value?.id || deleting.value) return
  const confirmed = window.confirm('确认删除这篇博客吗？')
  if (!confirmed) return

  deleting.value = true
  loadError.value = ''
  try {
    await axios.delete(`/api/blog/${blog.value.id}`)
    await router.push('/blog')
  } catch (error) {
    loadError.value = '删除失败，请稍后重试。'
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <section
    class="rounded-lg border border-stone-200 bg-white p-6 shadow-sm transition-all duration-300 transform hover:-translate-y-1 hover:scale-105 hover:shadow-md dark:border-stone-700 dark:bg-stone-800"
  >
    <p v-if="loading" class="text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">加载中...</p>
    <p v-else-if="loadError" class="text-sm text-rose-600">{{ loadError }}</p>

    <template v-else-if="blog">
      <div class="flex items-center justify-between gap-3">
        <h1 class="text-2xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">{{ blog.title }}</h1>
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

      <article class="mt-4 whitespace-pre-wrap text-sm leading-6 text-stone-700 transition-colors duration-300 dark:text-stone-300">{{ blog.content }}</article>

      <p class="mt-6 text-xs text-stone-500 transition-colors duration-300 dark:text-stone-400">
        创建时间：{{ blog.createdAt || '-' }} ｜ 更新时间：{{ blog.updatedAt || '-' }}
      </p>
    </template>

    <div class="mt-6 flex flex-wrap gap-4">
        <RouterLink
          to="/blog"
          class="inline-flex text-sm font-medium text-stone-700 underline-offset-2 transition-colors duration-300 hover:underline dark:text-stone-300"
        >
          返回博客列表
        </RouterLink>
      <RouterLink
        v-if="blog?.id"
        :to="`/blog/edit/${blog.id}`"
        class="inline-flex text-sm font-medium text-stone-700 underline-offset-2 transition-colors duration-300 hover:underline dark:text-stone-300"
      >
        前往编辑页面
      </RouterLink>
      <button
        v-if="blog?.id"
        class="inline-flex text-sm font-medium text-rose-600 underline-offset-2 hover:underline disabled:opacity-60"
        :disabled="deleting"
        @click="deleteBlog"
      >
        {{ deleting ? '删除中...' : '删除博客' }}
      </button>
    </div>
  </section>
</template>

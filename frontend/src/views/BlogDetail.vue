<script setup>
import axios from 'axios'
import { marked } from 'marked'
import { sanitizeMarkdownHtml, setupMarkdownRenderer } from '../utils/markdown'
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const blog = ref(null)
const loading = ref(true)
const loadError = ref('')
const deleting = ref(false)
const renderedContent = ref('')
const latestRenderVersion = ref(0)
setupMarkdownRenderer()

watch(
  () => blog.value?.content ?? '',
  (markdownText) => {
    const currentVersion = ++latestRenderVersion.value
    const parsed = marked.parse(markdownText, {
      gfm: true,
      breaks: true,
    })

    if (typeof parsed === 'string') {
      if (currentVersion !== latestRenderVersion.value) return
      renderedContent.value = sanitizeMarkdownHtml(parsed)
      return
    }

    parsed
      .then((rawHtml) => {
        if (currentVersion !== latestRenderVersion.value) return
        renderedContent.value = sanitizeMarkdownHtml(rawHtml)
      })
      .catch((error) => {
        if (currentVersion !== latestRenderVersion.value) return
        console.error('Markdown render failed:', error)
        renderedContent.value = ''
      })
  },
  { immediate: true },
)

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  if (Number.isNaN(date.getTime())) return timeStr

  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

async function fetchBlog() {
  loading.value = true
  loadError.value = ''
  blog.value = null
  try {
    const { data } = await axios.get(`/api/blog/${route.params.id}`)
    blog.value = data?.data ?? null
    if (!blog.value) {
      loadError.value = '博客数据格式错误，请稍后重试。'
    }
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
    class="rounded-lg border border-stone-200 bg-white p-4 shadow-sm dark:border-stone-700 dark:bg-stone-800 md:p-6"
  >
    <p v-if="loading" class="text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">加载中...</p>
    <p v-else-if="loadError" class="text-sm text-rose-600">{{ loadError }}</p>

    <template v-else-if="blog">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 class="text-xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100 md:text-2xl">{{ blog.title }}</h1>
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

      <article
        class="prose prose-sm prose-stone prose-headings:font-semibold prose-li:my-1 prose-code:bg-gray-100 prose-code:text-red-500 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none mt-4 max-w-none transition-colors duration-300 md:prose-base dark:prose-invert dark:prose-code:bg-gray-800 dark:prose-code:text-pink-400"
        aria-label="Blog post content"
        v-html="renderedContent"
      />

      <p class="mt-6 text-sm text-gray-500 transition-colors duration-300 dark:text-gray-400">
        📅 创建：{{ formatTime(blog.createdAt) }}<br>
        🔄 更新：{{ formatTime(blog.updatedAt) }}
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

<style scoped>
:deep(.prose pre) {
  background-color: #1f2937 !important;
  color: #f3f4f6 !important;
  border-radius: 0.5rem;
  overflow-x: auto;
  max-width: 100%;
  -webkit-overflow-scrolling: touch;
}

:deep(.dark .prose pre) {
  background-color: #111827 !important;
}

:deep(.prose pre code) {
  background-color: transparent !important;
  padding: 0 !important;
}
</style>

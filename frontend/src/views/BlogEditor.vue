<script setup>
import axios from 'axios'
import { marked } from 'marked'
import { sanitizeMarkdownHtml, setupMarkdownRenderer } from '../utils/markdown'
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => Boolean(route.params.id))
const backToListPath = computed(() => {
  const from = route.query.from
  return typeof from === 'string' && from.startsWith('/blog') ? from : '/blog'
})

const loading = ref(false)
const submitLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const previewHtml = ref('')
const previewVersionCounter = ref(0)
setupMarkdownRenderer()

const form = ref({
  title: '',
  content: '',
  tagsText: '',
  isFavorite: false,
})

watch(
  () => form.value.content,
  (markdownText) => {
    const currentVersion = ++previewVersionCounter.value
    const parsed = marked.parse(markdownText, {
      gfm: true,
      breaks: true,
    })

    if (typeof parsed === 'string') {
      if (currentVersion !== previewVersionCounter.value) return
      previewHtml.value = sanitizeMarkdownHtml(parsed)
      return
    }

    parsed
      .then((rawHtml) => {
        if (currentVersion !== previewVersionCounter.value) return
        previewHtml.value = sanitizeMarkdownHtml(rawHtml)
      })
      .catch((error) => {
        if (currentVersion !== previewVersionCounter.value) return
        console.error('Markdown preview render failed:', error)
        previewHtml.value = ''
      })
  },
  { immediate: true },
)

function normalizeTags(value) {
  if (!value) return []
  return value
    .replaceAll('，', ',')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

async function fetchBlogForEdit() {
  if (!isEdit.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await axios.get('/api/blog/', { params: { id: route.params.id } })
    const blog = data?.data ?? {}
    form.value.title = blog?.title ?? ''
    form.value.content = blog?.content ?? ''
    form.value.tagsText = Array.isArray(blog?.tags) ? blog.tags.join(', ') : ''
    form.value.isFavorite = Boolean(blog?.isFavorite)
  } catch (error) {
    errorMessage.value = '博客加载失败，请返回列表重试。'
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!form.value.title.trim()) {
    errorMessage.value = '标题不能为空。'
    return
  }

  submitLoading.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      content: form.value.content,
      tags: normalizeTags(form.value.tagsText),
      isFavorite: form.value.isFavorite,
    }

    const { data } = isEdit.value
      ? await axios.put(`/api/blog/${route.params.id}`, payload)
      : await axios.post('/api/blog', payload)

    const targetId = isEdit.value ? route.params.id : data?.data?.id
    if (!targetId) {
      throw new Error('missing_blog_id_in_response')
    }

    successMessage.value = isEdit.value ? '博客更新成功。' : '博客创建成功。'
    await router.push(`/blog/${targetId}`)
  } catch (error) {
    errorMessage.value = isEdit.value ? '更新失败，请稍后重试。' : '创建失败，请稍后重试。'
  } finally {
    submitLoading.value = false
  }
}

onMounted(fetchBlogForEdit)
</script>

<template>
  <section class="rounded-lg border border-stone-200 bg-white p-6 transition-colors duration-300 dark:border-stone-700 dark:bg-stone-800">
    <h1 class="text-2xl font-semibold text-stone-800 transition-colors duration-300 dark:text-stone-100">
      {{ isEdit ? '编辑博客' : '新建博客' }}
    </h1>

    <p v-if="loading" class="mt-4 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">加载中...</p>
    <p v-if="errorMessage" class="mt-4 text-sm text-rose-600">{{ errorMessage }}</p>
    <p v-if="successMessage" class="mt-4 text-sm text-emerald-600">{{ successMessage }}</p>

    <form v-if="!loading" class="mt-4 grid gap-4" @submit.prevent="submitForm">
      <label class="grid gap-1 text-sm text-stone-700 transition-colors duration-300 dark:text-stone-300">
        标题
        <input
          v-model="form.title"
          type="text"
          class="rounded border border-stone-300 bg-white px-3 py-2 text-stone-800 outline-none transition-colors duration-300 focus:border-stone-500 dark:border-stone-600 dark:bg-stone-900 dark:text-stone-100 dark:focus:border-stone-400"
          maxlength="120"
        />
      </label>

      <label class="grid gap-1 text-sm text-stone-700 transition-colors duration-300 dark:text-stone-300">
        标签（逗号分隔）
        <input
          v-model="form.tagsText"
          type="text"
          class="rounded border border-stone-300 bg-white px-3 py-2 text-stone-800 outline-none transition-colors duration-300 focus:border-stone-500 dark:border-stone-600 dark:bg-stone-900 dark:text-stone-100 dark:focus:border-stone-400"
        />
      </label>

      <div class="grid gap-4 md:grid-cols-2">
        <label class="grid gap-1 text-sm text-stone-700 transition-colors duration-300 dark:text-stone-300">
          内容（Markdown）
          <textarea
            v-model="form.content"
            rows="14"
            class="min-h-80 rounded border border-stone-300 bg-white px-3 py-2 font-mono text-sm text-stone-800 outline-none transition-colors duration-300 focus:border-stone-500 dark:border-stone-600 dark:bg-stone-900 dark:text-stone-100 dark:focus:border-stone-400"
          />
        </label>

        <div class="grid gap-1 text-sm text-stone-700 transition-colors duration-300 dark:text-stone-300">
          <span>预览</span>
          <article
            class="markdown-prose min-h-80 max-w-none rounded border border-stone-300 bg-white px-3 py-2 transition-colors duration-300 dark:border-stone-600 dark:bg-stone-900"
            v-html="previewHtml"
          />
        </div>
      </div>

      <label class="inline-flex items-center gap-2 text-sm text-stone-700 transition-colors duration-300 dark:text-stone-300">
        <input v-model="form.isFavorite" type="checkbox" />
        设为收藏
      </label>

      <div class="flex flex-wrap gap-3">
        <button
          type="submit"
          class="rounded border border-stone-300 bg-stone-800 px-4 py-2 text-sm font-medium text-white transition duration-300 disabled:opacity-60 dark:border-stone-600 dark:bg-stone-200 dark:text-stone-900 dark:hover:bg-stone-100"
          :disabled="submitLoading"
        >
          {{ submitLoading ? '提交中...' : isEdit ? '保存修改' : '创建博客' }}
        </button>
      </div>
    </form>

    <div class="mt-6 flex flex-wrap gap-4 text-sm">
      <RouterLink :to="backToListPath" class="font-medium text-stone-700 underline-offset-2 transition-colors duration-300 hover:underline dark:text-stone-300">
        返回博客列表
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => Boolean(route.params.id))

const loading = ref(false)
const submitLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = ref({
  title: '',
  content: '',
  tagsText: '',
  isFavorite: false,
})

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
    const { data } = await axios.get(`/api/blog/${route.params.id}`)
    form.value.title = data?.title ?? ''
    form.value.content = data?.content ?? ''
    form.value.tagsText = Array.isArray(data?.tags) ? data.tags.join(', ') : ''
    form.value.isFavorite = Boolean(data?.isFavorite)
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

    successMessage.value = isEdit.value ? '博客更新成功。' : '博客创建成功。'
    await router.push(`/blog/${data.id}`)
  } catch (error) {
    errorMessage.value = isEdit.value ? '更新失败，请稍后重试。' : '创建失败，请稍后重试。'
  } finally {
    submitLoading.value = false
  }
}

onMounted(fetchBlogForEdit)
</script>

<template>
  <section class="rounded-lg border border-stone-200 bg-white p-6">
    <h1 class="text-2xl font-semibold text-stone-800">
      {{ isEdit ? '编辑博客' : '新建博客' }}
    </h1>

    <p v-if="loading" class="mt-4 text-sm text-stone-500">加载中...</p>
    <p v-if="errorMessage" class="mt-4 text-sm text-rose-600">{{ errorMessage }}</p>
    <p v-if="successMessage" class="mt-4 text-sm text-emerald-600">{{ successMessage }}</p>

    <form v-if="!loading" class="mt-4 grid gap-4" @submit.prevent="submitForm">
      <label class="grid gap-1 text-sm text-stone-700">
        标题
        <input
          v-model="form.title"
          type="text"
          class="rounded border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
          maxlength="120"
        />
      </label>

      <label class="grid gap-1 text-sm text-stone-700">
        标签（逗号分隔）
        <input
          v-model="form.tagsText"
          type="text"
          class="rounded border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
        />
      </label>

      <label class="grid gap-1 text-sm text-stone-700">
        内容
        <textarea
          v-model="form.content"
          rows="8"
          class="rounded border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
        />
      </label>

      <label class="inline-flex items-center gap-2 text-sm text-stone-700">
        <input v-model="form.isFavorite" type="checkbox" />
        设为收藏
      </label>

      <div class="flex flex-wrap gap-3">
        <button
          type="submit"
          class="rounded border border-stone-300 bg-stone-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          :disabled="submitLoading"
        >
          {{ submitLoading ? '提交中...' : isEdit ? '保存修改' : '创建博客' }}
        </button>
      </div>
    </form>

    <div class="mt-6 flex flex-wrap gap-4 text-sm">
      <RouterLink to="/blog" class="font-medium text-stone-700 underline-offset-2 hover:underline">
        返回博客列表
      </RouterLink>
    </div>
  </section>
</template>

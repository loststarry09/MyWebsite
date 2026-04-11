<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { programs } from '../data/programs'

const showAddModal = ref(false)
const customPrograms = ref([])
const form = ref({
  name: '',
  description: '',
  techStack: '',
  status: '',
  api: '',
})
const touched = ref(false)

const allPrograms = computed(() => [...customPrograms.value, ...programs])

const errors = computed(() => ({
  name: form.value.name.length > 30 ? '项目名称不能超过 30 字' : '',
  description: form.value.description.length > 100 ? '项目描述不能超过 100 字' : '',
}))

const canSubmit = computed(
  () =>
    form.value.name.trim() &&
    form.value.description.trim() &&
    form.value.techStack.trim() &&
    form.value.status.trim() &&
    form.value.api.trim() &&
    !errors.value.name &&
    !errors.value.description,
)

function resetForm() {
  form.value = {
    name: '',
    description: '',
    techStack: '',
    status: '',
    api: '',
  }
  touched.value = false
}

function closeModal() {
  showAddModal.value = false
  resetForm()
}

function submitForm() {
  touched.value = true
  if (!canSubmit.value) return

  const stack = form.value.techStack
    .split(/[，,]/)
    .map((item) => item.trim())
    .filter(Boolean)

  customPrograms.value.unshift({
    id: `custom-${Date.now()}`,
    name: form.value.name.trim(),
    summary: form.value.description.trim(),
    stack,
    status: form.value.status.trim(),
    api: form.value.api.trim(),
    isCustom: true,
  })
  closeModal()
}
</script>

<template>
  <section class="rounded-xl border border-stone-200 bg-[#F7F5F2] p-6 shadow-sm transition hover:shadow-md">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-stone-800">我的程序</h1>
        <p class="mt-2 text-sm text-stone-500">这里收录我正在做或计划中的小项目。</p>
      </div>
      <button
        type="button"
        class="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
        @click="showAddModal = true"
      >
        + 添加项目
      </button>
    </div>

    <div class="mt-6 grid gap-4 sm:grid-cols-2">
      <article
        v-for="program in allPrograms"
        :key="program.id"
        class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
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
        <p v-if="program.api" class="mt-3 text-xs text-stone-500">
          接口：<span class="break-all text-stone-700">{{ program.api }}</span>
        </p>
        <RouterLink
          v-if="!program.isCustom"
          :to="`/program/${program.id}`"
          class="mt-4 inline-flex text-sm font-medium text-stone-700 underline-offset-2 hover:underline"
        >
          查看详情
        </RouterLink>
      </article>
    </div>

    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/35 p-4"
      @click.self="closeModal"
    >
      <div class="w-full max-w-lg rounded-xl border border-stone-200 bg-[#F7F5F2] p-5 shadow-xl">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-stone-800">添加项目</h2>
          <button
            type="button"
            class="rounded border border-stone-300 px-2 py-1 text-xs text-stone-600 hover:bg-stone-100"
            @click="closeModal"
          >
            关闭
          </button>
        </div>

        <form class="mt-4 space-y-3" @submit.prevent="submitForm">
          <div>
            <label class="mb-1 block text-sm text-stone-700">项目名称（30字以内）</label>
            <input
              v-model="form.name"
              maxlength="30"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.name.trim()" class="mt-1 text-xs text-rose-500">请输入项目名称</p>
            <p v-else-if="errors.name" class="mt-1 text-xs text-rose-500">{{ errors.name }}</p>
          </div>

          <div>
            <label class="mb-1 block text-sm text-stone-700">项目描述（100字以内）</label>
            <textarea
              v-model="form.description"
              maxlength="100"
              rows="3"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.description.trim()" class="mt-1 text-xs text-rose-500">
              请输入项目描述
            </p>
            <p v-else-if="errors.description" class="mt-1 text-xs text-rose-500">
              {{ errors.description }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm text-stone-700">技术栈</label>
            <input
              v-model="form.techStack"
              placeholder="例如：Vue 3, Flask"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.techStack.trim()" class="mt-1 text-xs text-rose-500">请输入技术栈</p>
          </div>

          <div>
            <label class="mb-1 block text-sm text-stone-700">项目状态</label>
            <input
              v-model="form.status"
              placeholder="例如：进行中"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.status.trim()" class="mt-1 text-xs text-rose-500">请输入项目状态</p>
          </div>

          <div>
            <label class="mb-1 block text-sm text-stone-700">后端接口地址</label>
            <input
              v-model="form.api"
              placeholder="例如：http://127.0.0.1:5000/api/programs"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.api.trim()" class="mt-1 text-xs text-rose-500">
              请输入后端接口地址
            </p>
          </div>

          <div class="pt-1 text-right">
            <button
              type="submit"
              class="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
            >
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

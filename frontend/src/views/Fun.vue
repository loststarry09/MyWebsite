<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'

const quotes = [
  '写点代码，也别忘了抬头看看天空。',
  '小步快跑，比原地完美更重要。',
  '今天的 1% 改进，就是未来的大差距。',
  '把复杂问题拆小，事情就会变简单。',
  '休息一下，灵感往往在路上出现。',
]

const currentQuote = ref(quotes[0])
const dice = ref(1)
const guess = ref('')
const resultText = ref('')
const showAddModal = ref(false)
const touched = ref(false)
const submitting = ref(false)
const submitNotice = ref({ type: '', message: '' })
const funItems = ref([])
const hasLoadedFunItems = ref(false)
const form = ref({
  name: '',
  description: '',
  api: '',
})

function randomInt(max) {
  return Math.floor(Math.random() * max)
}

function nextQuote() {
  currentQuote.value = quotes[randomInt(quotes.length)]
}

function rollDice() {
  dice.value = randomInt(6) + 1
  const guessed = Number(guess.value)
  if (!Number.isNaN(guessed) && guessed >= 1 && guessed <= 6) {
    resultText.value = guessed === dice.value ? '猜中了！🎉' : `没猜中，这次是 ${dice.value}`
  } else {
    resultText.value = `骰子结果：${dice.value}`
  }
}

function resetForm() {
  form.value = {
    name: '',
    description: '',
    api: '',
  }
  touched.value = false
}

function closeModal() {
  showAddModal.value = false
  resetForm()
}

async function fetchFunItems() {
  const { data } = await axios.get('/api/fun')
  funItems.value = Array.isArray(data) ? data : []
  hasLoadedFunItems.value = true
}

function createFunItem(payload) {
  return {
    id: `fun-${Date.now()}`,
    name: payload.name,
    description: payload.description,
    api: payload.api,
  }
}

async function submitFun() {
  touched.value = true
  if (
    submitting.value ||
    !form.value.name.trim() ||
    !form.value.description.trim() ||
    !form.value.api.trim() ||
    form.value.name.length > 30 ||
    form.value.description.length > 100
  ) {
    return
  }

  submitting.value = true
  submitNotice.value = { type: '', message: '' }
  const payload = {
    name: form.value.name.trim(),
    description: form.value.description.trim(),
    api: form.value.api.trim(),
  }

  try {
    await axios.post('/api/fun', payload)
    try {
      await fetchFunItems()
    } catch {
      funItems.value.unshift(createFunItem(payload))
    }
    submitNotice.value = { type: 'success', message: '娱乐项添加成功' }
    closeModal()
  } catch (error) {
    const message = error?.response?.data?.message || '娱乐项添加失败，请稍后重试'
    submitNotice.value = { type: 'error', message }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    await fetchFunItems()
  } catch {
    hasLoadedFunItems.value = false
  }
})
</script>

<template>
  <section class="rounded-xl border border-stone-200 bg-[#F7F5F2] p-6 shadow-sm transition hover:shadow-md">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-stone-800">娱乐</h1>
        <p class="mt-2 text-sm text-stone-500">轻松一下：随机一句话 + 猜骰子小游戏。</p>
      </div>
      <button
        type="button"
        class="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
        @click="showAddModal = true"
      >
        + 添加娱乐
      </button>
    </div>

    <div class="mt-6 grid gap-4 md:grid-cols-2">
      <article class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow">
        <h2 class="text-sm font-medium text-stone-700">今日随机一句</h2>
        <p class="mt-3 min-h-12 text-sm text-stone-600">{{ currentQuote }}</p>
        <button
          type="button"
          class="mt-3 rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 hover:bg-stone-50"
          @click="nextQuote"
        >
          换一句
        </button>
      </article>

      <article class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow">
        <h2 class="text-sm font-medium text-stone-700">猜骰子</h2>
        <div class="mt-3 flex items-center gap-2">
          <label for="guess-input" class="text-sm text-stone-600">猜 1~6：</label>
          <input
            id="guess-input"
            v-model="guess"
            inputmode="numeric"
            placeholder="例如 3"
            class="w-24 rounded border border-stone-300 px-2 py-1 text-sm outline-none focus:border-stone-500"
          />
          <button
            type="button"
            class="rounded border border-stone-300 px-3 py-1 text-sm text-stone-700 hover:bg-stone-50"
            @click="rollDice"
          >
            掷骰子
          </button>
        </div>
        <p class="mt-3 text-sm text-stone-600">{{ resultText || '输入数字后开始。' }}</p>
      </article>
    </div>

    <article
      class="mt-6 rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
    >
      <h2 class="text-sm font-medium text-stone-700">我添加的娱乐项</h2>
      <p v-if="!funItems.length" class="mt-2 text-sm text-stone-500">
        {{ hasLoadedFunItems ? '后端暂无数据。' : '暂未添加，点击右上角按钮开始。' }}
      </p>

      <ul v-else class="mt-3 space-y-3">
        <li
          v-for="item in funItems"
          :key="item.id"
          class="rounded-lg border border-stone-200 bg-[#F7F5F2] p-3"
        >
          <p class="text-sm font-medium text-stone-800">{{ item.name }}</p>
          <p class="mt-1 text-sm text-stone-600">{{ item.description }}</p>
          <p class="mt-2 text-xs text-stone-500">
            接口：<span class="break-all text-stone-700">{{ item.api }}</span>
          </p>
        </li>
      </ul>
    </article>

    <p
      v-if="submitNotice.message"
      class="mt-4 rounded-lg border px-3 py-2 text-sm"
      :class="
        submitNotice.type === 'success'
          ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
          : 'border-rose-200 bg-rose-50 text-rose-700'
      "
    >
      {{ submitNotice.message }}
    </p>

    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/35 p-4"
      @click.self="closeModal"
    >
      <div class="w-full max-w-lg rounded-xl border border-stone-200 bg-[#F7F5F2] p-5 shadow-xl">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-stone-800">添加娱乐</h2>
          <button
            type="button"
            class="rounded border border-stone-300 px-2 py-1 text-xs text-stone-600 hover:bg-stone-100"
            @click="closeModal"
          >
            关闭
          </button>
        </div>

        <form class="mt-4 space-y-3" @submit.prevent="submitFun">
          <div>
            <label class="mb-1 block text-sm text-stone-700">娱乐名称（30字以内）</label>
            <input
              v-model="form.name"
              maxlength="30"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.name.trim()" class="mt-1 text-xs text-rose-500">请输入娱乐名称</p>
            <p v-else-if="form.name.length > 30" class="mt-1 text-xs text-rose-500">
              娱乐名称不能超过 30 字
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm text-stone-700">描述（100字以内）</label>
            <textarea
              v-model="form.description"
              maxlength="100"
              rows="3"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.description.trim()" class="mt-1 text-xs text-rose-500">请输入描述</p>
            <p v-else-if="form.description.length > 100" class="mt-1 text-xs text-rose-500">
              描述不能超过 100 字
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm text-stone-700">后端接口地址</label>
            <input
              v-model="form.api"
              placeholder="例如：http://127.0.0.1:5000/api/fun"
              class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-stone-500"
            />
            <p v-if="touched && !form.api.trim()" class="mt-1 text-xs text-rose-500">
              请输入后端接口地址
            </p>
          </div>

          <div class="pt-1 text-right">
            <button
              type="submit"
              :disabled="submitting"
              class="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:-translate-y-0.5 hover:shadow"
            >
              {{ submitting ? '提交中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

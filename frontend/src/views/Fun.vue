<script setup>
import { ref } from 'vue'

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
</script>

<template>
  <section class="rounded-lg border border-stone-200 bg-white p-6">
    <h1 class="text-2xl font-semibold text-stone-800">娱乐</h1>
    <p class="mt-2 text-sm text-stone-500">轻松一下：随机一句话 + 猜骰子小游戏。</p>

    <div class="mt-6 grid gap-4 md:grid-cols-2">
      <article class="rounded-lg border border-stone-200 p-4">
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

      <article class="rounded-lg border border-stone-200 p-4">
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
  </section>
</template>

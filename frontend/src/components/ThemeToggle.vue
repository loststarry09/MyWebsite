<template>
  <div
    class="ml-auto inline-flex rounded-lg border border-gray-300 bg-white/60 p-1 shadow-sm transition-colors duration-300 dark:border-gray-700 dark:bg-gray-800/70"
  >
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="rounded-md px-2.5 py-1.5 text-xs font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-400 active:scale-95 dark:focus-visible:ring-stone-500"
      :aria-pressed="theme === option.value"
      :title="`切换到${option.label}模式`"
      :class="
        theme === option.value
          ? 'bg-gray-900 text-white shadow-sm ring-1 ring-gray-900/10 dark:bg-gray-100 dark:text-gray-900 dark:ring-gray-100/20'
          : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100'
      "
      @click="setTheme(option.value)"
    >
      <span class="inline-flex items-center gap-1.5">
        <span aria-hidden="true">{{ option.icon }}</span>
        <span>{{ option.label }}</span>
      </span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  theme: {
    type: String,
    required: true,
  },
  applyTheme: {
    type: Function,
    required: true,
  },
  themeStorageKey: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['theme-change'])

const options = [
  { label: 'Light', value: 'light', icon: '🌞' },
  { label: 'Dark', value: 'dark', icon: '🌙' },
  { label: 'System', value: 'system', icon: '💻' },
]

const setTheme = (theme) => {
  localStorage.setItem(props.themeStorageKey, theme)
  props.applyTheme(theme)
  emit('theme-change', theme)
}
</script>

<template>
  <div class="ml-auto inline-flex rounded-md border border-gray-300 p-1 dark:border-gray-700">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="rounded px-2 py-1 text-xs"
      :class="
        theme === option.value
          ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900'
          : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
      "
      @click="setTheme(option.value)"
    >
      {{ option.label }}
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
  { label: 'Light', value: 'light' },
  { label: 'Dark', value: 'dark' },
  { label: 'System', value: 'system' },
]

const setTheme = (theme) => {
  localStorage.setItem(props.themeStorageKey, theme)
  props.applyTheme(theme)
  emit('theme-change', theme)
}
</script>

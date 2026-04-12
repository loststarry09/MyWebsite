<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  to: {
    type: String,
    default: '',
  },
  href: {
    type: String,
    default: '',
  },
  external: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <component
    :is="external ? 'a' : 'RouterLink'"
    :href="external ? href : undefined"
    :to="!external ? to : undefined"
    :target="external ? '_blank' : undefined"
    :rel="external ? 'noopener noreferrer' : undefined"
    class="block rounded-xl border border-stone-200 bg-white p-6 text-left shadow-sm transition-colors duration-300 hover:border-stone-300 dark:border-stone-700 dark:bg-stone-800 dark:hover:border-stone-600"
  >
    <h2 class="text-lg font-medium text-stone-800 transition-colors duration-300 dark:text-stone-100">{{ title }}</h2>
    <p v-if="subtitle" class="mt-2 text-sm text-stone-500 transition-colors duration-300 dark:text-stone-400">{{ subtitle }}</p>
  </component>
</template>

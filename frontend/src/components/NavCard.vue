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
    class="block rounded-xl border border-stone-200 bg-white p-6 text-left shadow-sm transition-colors hover:border-stone-300"
  >
    <h2 class="text-lg font-medium text-stone-800">{{ title }}</h2>
    <p v-if="subtitle" class="mt-2 text-sm text-stone-500">{{ subtitle }}</p>
  </component>
</template>

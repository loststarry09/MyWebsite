<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <section class="rounded-lg border border-gray-200 bg-white p-6">
    <h1 class="text-2xl font-semibold">程序详情</h1>
    <p class="mt-2 text-sm text-gray-600">当前程序 ID：{{ route.params.id }}</p>
  </section>
</template>

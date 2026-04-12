<template>
  <div class="min-h-screen bg-[#F7F5F2] text-gray-800 dark:bg-gray-900 dark:text-gray-100">
    <header class="mx-auto flex max-w-4xl gap-4 px-6 py-6 text-sm">
      <RouterLink to="/" class="hover:underline">首页</RouterLink>
      <RouterLink to="/blog" class="hover:underline">博客</RouterLink>
      <RouterLink to="/programs" class="hover:underline">我的程序</RouterLink>
      <RouterLink to="/fun" class="hover:underline">娱乐</RouterLink>
      <ThemeToggle
        :theme="currentTheme"
        :theme-storage-key="THEME_STORAGE_KEY"
        :apply-theme="applyTheme"
        @theme-change="handleThemeChange"
      />
    </header>
    <main class="mx-auto max-w-4xl px-6 pb-10">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ThemeToggle from './components/ThemeToggle.vue'

const THEME_STORAGE_KEY = 'theme'
const DEFAULT_THEME = 'system'
const SYSTEM_THEME_QUERY = '(prefers-color-scheme: dark)'

const currentTheme = ref(DEFAULT_THEME)
let mediaQueryList

const getStoredTheme = () => {
  const storedTheme = localStorage.getItem(THEME_STORAGE_KEY)

  if (storedTheme === 'light' || storedTheme === 'dark' || storedTheme === 'system') {
    return storedTheme
  }

  return DEFAULT_THEME
}

const applyTheme = (theme) => {
  const root = document.documentElement
  const isSystemDark = window.matchMedia(SYSTEM_THEME_QUERY).matches

  if (theme === 'dark') {
    root.classList.add('dark')
    return
  }

  if (theme === 'light') {
    root.classList.remove('dark')
    return
  }

  if (isSystemDark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

const handleSystemThemeChange = () => {
  if (currentTheme.value === 'system') {
    applyTheme('system')
  }
}

const handleThemeChange = (theme) => {
  currentTheme.value = theme
}

onMounted(() => {
  currentTheme.value = getStoredTheme()
  applyTheme(currentTheme.value)

  mediaQueryList = window.matchMedia(SYSTEM_THEME_QUERY)
  mediaQueryList.addEventListener('change', handleSystemThemeChange)
})

onBeforeUnmount(() => {
  mediaQueryList?.removeEventListener('change', handleSystemThemeChange)
})
</script>
